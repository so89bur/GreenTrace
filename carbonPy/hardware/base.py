# carbon_py/hardware/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class HardwareMonitor(ABC):
    """Абстрактный базовый класс для мониторинга энергопотребления оборудования."""

    def __init__(self, max_measurements: Optional[int] = None):
        self._measurements: List[Tuple[datetime, float]] = []
        self.max_measurements = max_measurements

    @abstractmethod
    def start(self, silent: bool = False) -> None:
        """Начать мониторинг."""
        pass

    @abstractmethod
    def stop(self, silent: bool = False) -> None:
        """Остановить мониторинг."""
        pass

    @abstractmethod
    def get_power_usage(self) -> float:
        """Получить текущее энергопотребление в Ваттах."""
        pass

    def get_total_energy_kwh(self, interval_seconds: int) -> float:
        """
        Рассчитывает общую потребленную энергию в кВт*ч.

        Формула: (средняя_мощность_ватт * общее_время_секунд) / (1000 * 3600)
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
        """Добавляет измерение мощности с временной меткой."""
        self._measurements.append((datetime.now(), power_watts))

        if self.max_measurements and len(self._measurements) > self.max_measurements:
            self._measurements.pop(0)

    def get_metadata(self) -> Dict[str, str]:
        """Возвращает метаданные об оборудовании."""
        return {}
