import sys
import os
import time
import asyncio

# Add the project root directory to sys.path
# so that carbon_py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import track_emissions


@track_emissions(
    interval=2,
    region="US",
    output_file="report.csv",
    csv_summary_only=True,
    max_measurements=5,
    # output_strategy="timestamp",
    silent=False,
)
def short_sync_task():
    print("\nStarting sync task for CSV report...")
    time.sleep(20)
    print("Sync task finished.")


short_sync_task()
