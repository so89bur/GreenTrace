import sys
import os
import time
import asyncio
import threading

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from GreenTrace.tracker import EmissionsTracker, track_emissions, TrackerNotRunningError


@track_emissions(interval=1, region="FR", name="long_task")
def long_running_task():
    """A long-running task that we will monitor."""
    print("Starting long computations...")
    time.sleep(15)
    print("Long computations finished.")


def monitor_task():
    """Monitoring function, requests data every 3 seconds."""
    print("\n--- Monitoring started ---")
    while True:
        try:
            # Get the active tracker by its name
            tracker = EmissionsTracker.get_active_tracker("long_task")
            data = tracker.get_current_data()
            emissions = data["summary"]["emissions_gco2eq"]
            duration = data["summary"]["duration_seconds"]
            print(f"Intermediate result: {emissions:.4f} gCO₂eq in {duration:.2f} sec.")
            time.sleep(3)
        except TrackerNotRunningError:
            print("--- Monitoring finished (tracker stopped) ---\n")
            break


# Run the monitoring task in a separate thread
monitor_thread = threading.Thread(target=monitor_task)
monitor_thread.start()

# Run the main long-running task
long_running_task()

# Wait for the monitoring thread to finish
monitor_thread.join()
