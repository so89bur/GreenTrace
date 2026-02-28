import asyncio
import os
import time
import json
import csv

import pytest

from carbonPy.tracker import EmissionsTracker, track_emissions, TrackerNotRunningError

# Mark all tests in this file as async for pytest-asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def tracker_params(tmp_path):
    """Common parameters for the tracker in tests."""
    return {
        "interval_seconds": 0.05,
        "output_file": tmp_path / "report.json",
        "output_format": "json",
        "silent": False,
    }


class TestEmissionsTracker:
    """Tests for the EmissionsTracker class."""

    async def test_sync_context_manager(self, tracker_params):
        """Test synchronous operation with the context manager."""
        with EmissionsTracker(**tracker_params):
            time.sleep(0.16)

        output_file = tracker_params["output_file"]
        assert output_file.exists()
        with open(output_file, "r") as f:
            data = json.load(f)

        assert "summary" in data
        assert "measurements" in data
        # Expect 1 (initial) + 3 (0.16 / 0.05) = 4 measurements
        assert len(data["measurements"]) >= 3
        assert data["summary"]["carbon_intensity_gco2_per_kwh"]

    async def test_async_context_manager(self, tracker_params):
        """Test asynchronous operation with the context manager."""
        async with EmissionsTracker(**tracker_params):
            await asyncio.sleep(0.16)

        output_file = tracker_params["output_file"]
        assert output_file.exists()
        with open(output_file, "r") as f:
            data = json.load(f)

        assert len(data["measurements"]) >= 3
        assert data["summary"]["carbon_intensity_gco2_per_kwh"]

    async def test_max_measurements(self, tmp_path):
        """Test the measurement limit (max_measurements)."""
        params = {
            "interval_seconds": 0.02,
            "output_file": tmp_path / "report.json",
            "max_measurements": 5,
            "output_format": "json",
            "silent": True,
        }
        async with EmissionsTracker(**params):
            await asyncio.sleep(0.2)  # Should make ~10 measurements

        with open(params["output_file"], "r") as f:
            data = json.load(f)

        assert len(data["measurements"]) == 5


class TestTrackEmissionsDecorator:
    """Tests for the @track_emissions decorator."""

    async def test_sync_decorator(self, tmp_path):
        """Test the decorator on a synchronous function."""
        output_file = tmp_path / "sync_report.csv"

        @track_emissions(
            interval=0.05, output_file=output_file, silent=True, region="FR"
        )
        def sync_task():
            # time.sleep() is correct here because the function itself is synchronous
            time.sleep(0.11)

        await asyncio.to_thread(sync_task)

        assert output_file.exists()
        with open(output_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) >= 3  # Header + at least 2 measurements

    async def test_async_decorator(self, tmp_path):
        """Test the decorator on an asynchronous function."""
        output_file = tmp_path / "async_report.html"

        @track_emissions(
            interval=0.05, output_file=output_file, silent=True, region="DE"
        )
        async def async_task():
            await asyncio.sleep(0.11)

        await async_task()

        assert output_file.exists()
        content = output_file.read_text()
        assert "Carbon Footprint Certificate" in content
        assert "DE" in content

    async def test_output_strategy_timestamp(self, tmp_path):
        """Test the timestamp file naming strategy."""
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
        await asyncio.sleep(1)  # Make sure the timestamps will be different
        await asyncio.to_thread(task)

        files = list(tmp_path.glob("report_*.json"))
        assert len(files) == 2


class TestMonitoring:
    """Tests for real-time monitoring functionality."""

    async def test_get_active_tracker(self):
        """Test getting intermediate data from an active tracker."""
        tracker_name = "my_long_task"

        @track_emissions(interval=0.05, name=tracker_name, silent=True)
        async def long_task():
            # Give the tracker time to start
            await asyncio.sleep(0.06)

            # Get intermediate data
            tracker = EmissionsTracker.get_active_tracker(tracker_name)
            data = tracker.get_current_data()
            assert data["summary"]["duration_seconds"] > 0
            assert len(data["measurements"]) > 0

            await asyncio.sleep(0.1)

        await long_task()

        # Check that the tracker is removed from active trackers after completion
        with pytest.raises(TrackerNotRunningError):
            EmissionsTracker.get_active_tracker(tracker_name)


class TestReporting:
    """Tests for report generation."""

    async def test_csv_summary_only(self, tmp_path):
        """Test saving only summary data to CSV."""
        output_file = tmp_path / "summary.csv"

        @track_emissions(
            interval=0.02,
            output_file=output_file,
            csv_summary_only=True,
            silent=True,
        )
        def task():
            time.sleep(0.1)  # time.sleep() is correct here

        await asyncio.to_thread(task)

        assert output_file.exists()
        with open(output_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # Header + one summary row
            assert "total_energy_kwh" in rows[0]
