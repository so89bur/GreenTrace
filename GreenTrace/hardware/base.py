# GreenTrace/hardware/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class HardwareMonitor(ABC):
    """Abstract base class for monitoring hardware power consumption."""

    def __init__(self):
        pass

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

    def get_metadata(self) -> Dict[str, str]:
        """Returns metadata about the hardware."""
        return {}
