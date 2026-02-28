import sys
import os
import time
import asyncio

# Add the project root directory to sys.path
# so that carbon_py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import track_emissions


@track_emissions(interval=1, region="DE")
def process_data():
    print("Starting heavy computations...")
    # Simulate CPU work
    _ = [i * i for i in range(20_000_000)]
    time.sleep(3)
    print("Computations finished.")


process_data()
