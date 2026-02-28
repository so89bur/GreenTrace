import sys
import os
import time
import asyncio

# Add the project root directory to sys.path
# so that carbon_py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import track_emissions


@track_emissions(interval=1, region="FR", output_file="async_report.html")
async def async_process_data():
    print("Starting asynchronous computations...")
    await asyncio.sleep(10)
    print("Computations finished.")


asyncio.run(async_process_data())
