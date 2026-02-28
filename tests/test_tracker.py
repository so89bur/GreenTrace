import asyncio
import os
import time
import json
import csv

import pytest

from carbonPy.tracker import EmissionsTracker, track_emissions, TrackerNotRunningError

# Помечаем все тесты в файле как асинхронные для pytest-asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def tracker_params(tmp_path):
    """Общие параметры для трекера в тестах."""
    return {
        "interval_seconds": 0.05,
        "output_file": tmp_path / "report.json",
        "output_format": "json",
        "silent": False,
    }


class TestEmissionsTracker:
    """Тесты для класса EmissionsTracker."""

    async def test_sync_context_manager(self, tracker_params):
        """Тестирование синхронной работы с менеджером контекста."""
        with EmissionsTracker(**tracker_params):
            time.sleep(0.16)

        output_file = tracker_params["output_file"]
        assert output_file.exists()
        with open(output_file, "r") as f:
            data = json.load(f)

        assert "summary" in data
        assert "measurements" in data
        # Ожидаем 1 (начальный) + 3 (0.16 / 0.05) = 4 измерения
        assert len(data["measurements"]) >= 3
        assert data["summary"]["carbon_intensity_gco2_per_kwh"]

    async def test_async_context_manager(self, tracker_params):
        """Тестирование асинхронной работы с менеджером контекста."""
        async with EmissionsTracker(**tracker_params):
            await asyncio.sleep(0.16)

        output_file = tracker_params["output_file"]
        assert output_file.exists()
        with open(output_file, "r") as f:
            data = json.load(f)

        assert len(data["measurements"]) >= 3
        assert data["summary"]["carbon_intensity_gco2_per_kwh"]

    async def test_max_measurements(self, tmp_path):
        """Тестирование ограничения количества измерений (max_measurements)."""
        params = {
            "interval_seconds": 0.02,
            "output_file": tmp_path / "report.json",
            "max_measurements": 5,
            "output_format": "json",
            "silent": True,
        }
        async with EmissionsTracker(**params):
            await asyncio.sleep(0.2)  # Должно быть сделано ~10 измерений

        with open(params["output_file"], "r") as f:
            data = json.load(f)

        assert len(data["measurements"]) == 5


class TestTrackEmissionsDecorator:
    """Тесты для декоратора @track_emissions."""

    async def test_sync_decorator(self, tmp_path):
        """Тестирование декоратора на синхронной функции."""
        output_file = tmp_path / "sync_report.csv"

        @track_emissions(
            interval=0.05, output_file=output_file, silent=True, region="FR"
        )
        def sync_task():
            time.sleep(
                0.11
            )  # Здесь time.sleep() корректен, т.к. сама функция синхронная

        await asyncio.to_thread(sync_task)

        assert output_file.exists()
        with open(output_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) >= 3  # Заголовок + минимум 2 измерения

    async def test_async_decorator(self, tmp_path):
        """Тестирование декоратора на асинхронной функции."""
        output_file = tmp_path / "async_report.html"

        @track_emissions(
            interval=0.05, output_file=output_file, silent=True, region="DE"
        )
        async def async_task():
            await asyncio.sleep(0.11)

        await async_task()

        assert output_file.exists()
        content = output_file.read_text()
        assert "Сертификат Углеродного Следа" in content
        assert "DE" in content

    async def test_output_strategy_timestamp(self, tmp_path):
        """Тестирование стратегии именования файлов с временной меткой."""
        output_file = tmp_path / "report.json"

        @track_emissions(
            interval=0.01,
            output_file=output_file,
            output_strategy="timestamp",
            silent=True,
        )
        def task():
            time.sleep(0.02)

        await asyncio.to_thread(task)
        await asyncio.sleep(1)  # Убедимся, что временные метки будут разными
        await asyncio.to_thread(task)

        files = list(tmp_path.glob("report_*.json"))
        assert len(files) == 2


class TestMonitoring:
    """Тесты для функциональности мониторинга в реальном времени."""

    async def test_get_active_tracker(self):
        """Тестирование получения промежуточных данных из активного трекера."""
        tracker_name = "my_long_task"

        @track_emissions(interval=0.05, name=tracker_name, silent=True)
        async def long_task():
            # Даем время трекеру запуститься
            await asyncio.sleep(0.06)

            # Получаем промежуточные данные
            tracker = EmissionsTracker.get_active_tracker(tracker_name)
            data = tracker.get_current_data()
            assert data["summary"]["duration_seconds"] > 0
            assert len(data["measurements"]) > 0

            await asyncio.sleep(0.1)

        await long_task()

        # Проверяем, что трекер удаляется из активных после завершения
        with pytest.raises(TrackerNotRunningError):
            EmissionsTracker.get_active_tracker(tracker_name)


class TestReporting:
    """Тесты для генерации отчетов."""

    async def test_csv_summary_only(self, tmp_path):
        """Тестирование сохранения в CSV только итоговых данных."""
        output_file = tmp_path / "summary.csv"

        @track_emissions(
            interval=0.02,
            output_file=output_file,
            csv_summary_only=True,
            silent=True,
        )
        def task():
            time.sleep(0.1)  # Здесь time.sleep() корректен

        await asyncio.to_thread(task)

        assert output_file.exists()
        with open(output_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Заголовок + одна строка с итогами
            assert "total_energy_kwh" in rows[0]
