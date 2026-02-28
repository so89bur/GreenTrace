# GreenTrace/hardware/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class HardwareMonitor(ABC):
    """Abstract base class for monitoring hardware power consumption."""

    def __init__(self, max_measurements: Optional[int] = None):
        self._measurements: List[Tuple[datetime, float]] = []
        self.max_measurements = max_measurements

    @abstractmethod
    def start(self, silent: bool = False) -> None:
        """Start monitoring."""
        pass

    @abstractmethod
    def stop(self, silent: bool = False) -> None:
        """Stop monitoring."""
        pass

    @abstractmethod
    def get_power_usage(self) -> float:
        """Get the current power consumption in Watts."""
        pass

    def get_total_energy_kwh(self, interval_seconds: int) -> float:
        """
        Calculates the total energy consumed in kWh.

        Formula: (average_power_watts * total_seconds) / (1000 * 3600)
        """
        if not self._measurements:
            return 0.0

        avg_power_watts = sum(power for _, power in self._measurements) / len(
            self._measurements
        )
        total_seconds = len(self._measurements) * interval_seconds

        kwh = (avg_power_watts * total_seconds) / (1000 * 3600)
        return kwh

    def add_measurement(self, power_watts: float):
        """Adds a power measurement with a timestamp."""
        self._measurements.append((datetime.now(), power_watts))

        if self.max_measurements and len(self._measurements) > self.max_measurements:
            self._measurements.pop(0)

    def get_metadata(self) -> Dict[str, str]:
        """Returns metadata about the hardware."""
        return {}
