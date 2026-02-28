# carbon_py/hardware/cpu.py

import os
import platform
import time
import psutil
from typing import Optional, Dict

import cpuinfo

from .base import HardwareMonitor

# Data source for TDP/Max Power:
# Intel/AMD: Data from manufacturers and benchmarks.
CPU_POWER_DATA: Dict[str, float] = {
    # Apple Silicon (Max Power, W)
    "Apple M1": 20.0,
    "Apple M1 Pro": 40.0,
    "Apple M1 Max": 90.0,
    "Apple M1 Ultra": 150.0,
    "Apple M2": 25.0,
    "Apple M2 Pro": 50.0,
    "Apple M2 Max": 100.0,
    "Apple M2 Ultra": 160.0,
    "Apple M3": 28.0,
    "Apple M3 Pro": 60.0,
    "Apple M3 Max": 120.0,
    "Apple M4": 24.0,
    "Apple M4 Pro": 38.0,
    "Apple M4 Max": 70.0,
    # Intel Core (TDP, W)
    "Intel Core i9-13900K": 125.0,
    "Intel Core i7-13700K": 125.0,
    "Intel Core i5-13600K": 125.0,
    "Intel Core i9-12900K": 125.0,
    "Intel Core i7-12700K": 125.0,
    "Intel Core i5-12600K": 125.0,
    "Intel Core i9-11900K": 125.0,
    "Intel Core i7-11700K": 125.0,
    "Intel Core i5-11600K": 125.0,
    # AMD Ryzen (TDP, W)
    "AMD Ryzen 9 7950X": 170.0,
    "AMD Ryzen 7 7700X": 105.0,
    "AMD Ryzen 5 7600X": 105.0,
    "AMD Ryzen 9 5950X": 105.0,
    "AMD Ryzen 9 5900X": 105.0,
    "AMD Ryzen 7 5800X": 105.0,
    "AMD Ryzen 5 5600X": 65.0,
}

RAPL_DIR = "/sys/class/powercap/intel-rapl/"


class CPUMonitor(HardwareMonitor):
    """Monitors CPU power consumption."""

    def __init__(self, max_measurements: Optional[int] = None):
        super().__init__(max_measurements=max_measurements)
        self.tdp = 125.0  # Default value
        self.is_rapl_available = False
        self.rapl_energy_files = []
        self._last_rapl_energy = 0.0
        self._last_rapl_time = 0.0

    def start(self, silent: bool = False) -> None:
        self._measurements = []
        self._detect_cpu_power_source(silent)

        if self.is_rapl_available:
            self._last_rapl_energy = self._get_rapl_energy()
            self._last_rapl_time = time.time()
            if not silent:
                print("CPU Monitor: Started using Intel RAPL.")
        else:
            if not silent:
                print(f"CPU Monitor: Started using TDP model ({self.tdp}W).")

    def _detect_cpu_power_source(self, silent: bool):
        """Determines the data source: RAPL or TDP."""
        # 1. Check for Intel RAPL (Linux only)
        if platform.system() == "Linux" and os.path.exists(RAPL_DIR):
            for root, _, files in os.walk(RAPL_DIR):
                if "energy_uj" in files and "intel-rapl" in root:
                    self.rapl_energy_files.append(os.path.join(root, "energy_uj"))
            if self.rapl_energy_files:
                self.is_rapl_available = True
                return

        cpu_info = cpuinfo.get_cpu_info()
        brand = cpu_info.get("brand_raw", "")

        for name, power in CPU_POWER_DATA.items():
            if name.lower() in brand.lower():
                self.tdp = power
                if not silent:
                    print(f"CPU Monitor: Detected '{brand}', using {power}W.")
                return

        if not silent:
            print(
                f"CPU Monitor Warning: CPU '{brand}' not in database. "
                f"Falling back to default TDP ({self.tdp}W)."
            )

    def _get_rapl_energy(self) -> float:
        """Reads the total energy from all found RAPL files."""
        total_energy_uj = 0
        for file_path in self.rapl_energy_files:
            try:
                with open(file_path, "r") as f:
                    total_energy_uj += int(f.read())
            except (IOError, ValueError):
                continue
        return total_energy_uj

    def _get_power_from_rapl(self) -> float:
        """Calculates the average power over a time interval using RAPL."""
        current_energy = self._get_rapl_energy()
        current_time = time.time()

        time_delta = current_time - self._last_rapl_time
        energy_delta = current_energy - self._last_rapl_energy

        # Update values for the next call
        self._last_rapl_energy = current_energy
        self._last_rapl_time = current_time

        if time_delta == 0:
            return 0.0

        # Convert from microjoules to joules and divide by seconds to get Watts
        power_watts = (energy_delta / 1_000_000) / time_delta
        return power_watts if power_watts >= 0 else 0.0

    def _get_power_from_tdp(self) -> float:
        """Estimates power consumption based on TDP and CPU utilization."""
        cpu_utilization = psutil.cpu_percent() / 100.0
        power_watts = self.tdp * cpu_utilization
        return power_watts

    def stop(self, silent: bool = False) -> None:
        if not silent:
            print("CPU Monitor: Stopped")

    def get_power_usage(self) -> float:
        """Returns the current CPU power consumption in Watts."""
        if self.is_rapl_available:
            return self._get_power_from_rapl()
        else:
            return self._get_power_from_tdp()
