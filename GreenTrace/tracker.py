# GreenTrace/tracker.py

import time
import asyncio
import inspect
import os
from datetime import datetime
from threading import Thread
from functools import wraps
from typing import List, Optional

from .hardware.base import HardwareMonitor
from .hardware.cpu import CPUMonitor
from .emissions import CarbonIntensityProvider
from .reporting import Reporter


class TrackerNotRunningError(Exception):
    pass


class EmissionsTracker:
    """Main class for tracking emissions. Works in both synchronous and asynchronous modes."""

    def __init__(
        self,
        # TODO: add GPU
        hardware_monitors: Optional[List[HardwareMonitor]] = None,
        interval_seconds: int = 5,
        region: str = "DEFAULT",
        output_file: Optional[str] = None,
        output_format: str = "console",  # console, json, csv, html
        csv_summary_only: bool = False,
        max_measurements: Optional[int] = None,
        name: str = "default",
        silent: bool = False,
    ):
        print(output_file, output_format)
        self.hardware_monitors = hardware_monitors or [
            CPUMonitor(max_measurements=max_measurements)
        ]
        self.interval = interval_seconds
        self.region = region
        self.output_file = output_file
        self.output_format = output_format if output_file else "console"
        self.csv_summary_only = csv_summary_only
        self.silent = silent
        self.name = name
        self.max_measurements = max_measurements

        self._is_running = False
        self._task: Optional[Thread or asyncio.Task] = None
        self.total_energy_kwh = 0.0
        self.measurements: List[dict] = []
        self.emissions_gco2eq = 0.0
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self.carbon_intensity = CarbonIntensityProvider().get_intensity(self.region)

    _active_trackers: "dict[str, EmissionsTracker]" = {}

    def _measure(self):
        """Performs a single power measurement for all devices."""
        for monitor in self.hardware_monitors:
            power = monitor.get_power_usage()
            monitor.add_measurement(power)
            self._process_latest_measurement(monitor, power)

    def _process_latest_measurement(self, monitor: HardwareMonitor, power_watts: float):
        """Processes the latest measurement and adds it to self.measurements."""
        timestamp = datetime.now()
        energy_kwh = (power_watts * self.interval) / (1000 * 3600)
        self.total_energy_kwh += energy_kwh
        emissions_gco2eq = energy_kwh * self.carbon_intensity

        self.measurements.append(
            {
                "timestamp": timestamp.isoformat(),
                "duration_seconds": self.interval,
                "power_watts": round(power_watts, 4),
                "energy_kwh": round(energy_kwh, 9),
                "emissions_gco2eq": round(emissions_gco2eq, 6),
            }
        )
        # Apply the limit on the number of stored measurements
        if self.max_measurements and len(self.measurements) > self.max_measurements:
            self.measurements.pop(0)

    def _sync_run(self):
        """Measurement loop for synchronous code (in a separate thread)."""
        self._measure()  # First measurement right at the start
        while self._is_running:
            time.sleep(self.interval)
            self._measure()

    async def _async_run(self):
        """Measurement loop for asynchronous code."""
        self._measure()  # First measurement right at the start
        while self._is_running:
            await asyncio.sleep(self.interval)
            self._measure()

    def start(self):
        """Starts the tracker."""
        EmissionsTracker._active_trackers[self.name] = self
        self._start_time = datetime.now()
        self._is_running = True
        for monitor in self.hardware_monitors:
            monitor.start(silent=self.silent)

        self._task = Thread(target=self._sync_run)
        self._task.start()
        if not self.silent:
            print("Tracker: Running in SYNC mode (background thread).")

    def astart(self):
        """Starts the ASYNC tracker."""
        EmissionsTracker._active_trackers[self.name] = self
        self._start_time = datetime.now()
        self._is_running = True
        for monitor in self.hardware_monitors:
            monitor.start(silent=self.silent)

        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._async_run())
        if not self.silent:
            print("Tracker: Running in ASYNC mode.")

    def stop(self):
        """Stops the tracker and calculates the results."""
        if not self._is_running:
            return

        self._is_running = False
        self._end_time = datetime.now()

        # Wait for the task to complete
        if isinstance(self._task, Thread):
            self._task.join(timeout=self.interval)
        elif isinstance(self._task, asyncio.Task):
            # In asynchronous mode, just cancel the task
            self._task.cancel()

        for monitor in self.hardware_monitors:
            monitor.stop(silent=self.silent)

        if self.name in EmissionsTracker._active_trackers:
            del EmissionsTracker._active_trackers[self.name]

        report_data = self.get_current_data()

        reporter = Reporter(
            data=report_data,
            output_file=self.output_file,
            output_format=self.output_format,
            csv_summary_only=self.csv_summary_only,
            silent=self.silent,
        )
        reporter.report()

    def get_current_data(self) -> dict:
        """Returns the current accumulated data."""
        if not self._is_running and not self._end_time:
            # Tracker has not been started yet
            end_time = None
        else:
            # Tracker is running or has been stopped
            end_time = self._end_time or datetime.now()

        duration_seconds = 0
        if self._start_time:
            current_end_time = self._end_time or datetime.now()
            duration_seconds = (current_end_time - self._start_time).total_seconds()

        total_emissions = self.total_energy_kwh * self.carbon_intensity
        return {
            "summary": {
                "start_time": (
                    self._start_time.isoformat() if self._start_time else None
                ),
                "end_time": end_time.isoformat() if end_time else None,
                "duration_seconds": round(duration_seconds, 2),
                "total_energy_kwh": round(self.total_energy_kwh, 6),
                "region": self.region,
                "carbon_intensity_gco2_per_kwh": self.carbon_intensity,
                "emissions_gco2eq": round(total_emissions, 4),
            },
            "measurements": self.measurements,
        }

    @classmethod
    def get_active_tracker(cls, name: str = "default") -> "EmissionsTracker":
        """Returns the active tracker instance by name."""
        tracker = cls._active_trackers.get(name)
        if not tracker:
            raise TrackerNotRunningError(
                f"Tracker with name '{name}' not found or not running."
            )
        return tracker

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    async def __aenter__(self):
        """Asynchronous entry into the context manager."""
        self.astart()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous exit from the context manager."""
        self.stop()


# --- Decorator ---
def track_emissions(
    func=None,
    *,
    interval: int = 5,
    region: str = "DEFAULT",
    output_file: Optional[str] = None,
    output_format: str = "console",
    csv_summary_only: bool = False,
    max_measurements: Optional[int] = None,
    output_strategy: str = "overwrite",  # overwrite, timestamp
    name: str = "default",
    silent: bool = False,
):
    def decorator(fn):
        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            format = output_format
            current_output_file = output_file

            if current_output_file:
                if output_strategy == "timestamp":
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    base, ext = os.path.splitext(current_output_file)
                    current_output_file = f"{base}_{timestamp}{ext}"

                _, ext = os.path.splitext(current_output_file)
                format = ext.lower().lstrip(".") if ext else "console"

            with EmissionsTracker(
                interval_seconds=interval,
                region=region,
                output_file=current_output_file,
                output_format=format,
                csv_summary_only=csv_summary_only,
                max_measurements=max_measurements,
                name=name,
                silent=silent,
            ):
                return fn(*args, **kwargs)

        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            format = output_format
            current_output_file = output_file

            if current_output_file:
                if output_strategy == "timestamp":
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    base, ext = os.path.splitext(current_output_file)
                    current_output_file = f"{base}_{timestamp}{ext}"

                _, ext = os.path.splitext(current_output_file)
                format = ext.lower().lstrip(".") if ext else "console"

            async with EmissionsTracker(
                interval_seconds=interval,
                region=region,
                output_file=current_output_file,
                output_format=format,
                csv_summary_only=csv_summary_only,
                max_measurements=max_measurements,
                name=name,
                silent=silent,
            ):
                # In async mode, the tracker will detect this and start an asyncio.Task
                result = await fn(*args, **kwargs)
            return result

        if inspect.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    if func:
        return decorator(func)
    return decorator
