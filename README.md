# 💡 GreenTrace: Effortless CO₂ Emissions Tracking for Python Code

[![PyPI version](https://badge.fury.io/py/GreenTrace.svg)](https://badge.fury.io/py/GreenTrace)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Track the carbon footprint of your Python functions and code blocks with ease. Works seamlessly in both synchronous and asynchronous applications.**

`GreenTrace` is a lightweight, simple, and powerful tool for measuring the energy consumption and estimating the CO₂ emissions of your Python code. It requires no external APIs, accounts, or permissions to get started. Just install, import, and add a decorator or a context manager.

---

## Key Features

*   **Effortless Integration:** Use a simple decorator (`@track_emissions`) or a context manager to start tracking without refactoring your code.
*   **Works Offline, No API Keys:** All carbon intensity data is included in the library. It works out-of-the-box without any network requests, API keys, or registration.
*   **Native Async Support:** `GreenTrace` is designed for modern Python and works flawlessly with `async` and `await` syntax, a feature often missing in other trackers.
*   **Lightweight with Minimal Dependencies:** Built to be lean, `GreenTrace` adds minimal overhead to your project.
*   **Accurate Hardware Monitoring:** On Linux, it uses **Intel's RAPL interface** for precise CPU energy readings where available. On other systems, it uses a reliable model based on CPU load and Thermal Design Power (TDP).
*   **Beautiful, Shareable Reports:** Generate reports as console output, JSON, CSV, or a stunning, self-contained **HTML certificate** perfect for sharing your results.

## Why track emissions?

Understanding the carbon footprint of your software is the first step toward building more sustainable and efficient applications. `GreenTrace` helps you:

-   **Benchmark** the efficiency of different algorithms.
-   **Identify** energy-hungry parts of your code.
-   **Promote** green coding practices in your team.
-   **Report** on the environmental impact of your computations.

---

## Installation

Install with your favorite package manager.

**Using `pip`:**
```bash
pip install GreenTrace
```

**Using `uv`:**
```bash
uv pip install GreenTrace
```

---

## How to Use

`GreenTrace` can be used as a decorator or a context manager.

### 1. As a Decorator

This is the simplest way. Just add `@track_emissions` to any function. It works for both `def` and `async def` functions automatically.

**For a standard synchronous function:**

```python
from GreenTrace import track_emissions
import time

@track_emissions(region="FR", output_format="console")
def my_heavy_computation():
    # This function performs some CPU-intensive work
    print("Running a heavy computation...")
    start_time = time.time()
    while time.time() - start_time < 10:
        _ = [i*i for i in range(10000)]
    print("Computation finished.")

if __name__ == "__main__":
    my_heavy_computation()
```

**For an asynchronous function:**

```python
import asyncio
from GreenTrace import track_emissions

@track_emissions(region="DE", output_file="async_report.html")
async def my_async_task():
    print("Starting async task...")
    await asyncio.sleep(5)
    print("Async task finished.")

if __name__ == "__main__":
    asyncio.run(my_async_task())
```

### 2. As a Context Manager

If you want to track a specific block of code instead of an entire function, use a context manager.

**Synchronous `with` block:**

```python
from GreenTrace import EmissionsTracker
import time

with EmissionsTracker(region="US", output_file="report.json"):
    print("Tracking a specific block of code...")
    time.sleep(3)
    # ... your code here ...
    print("Block finished.")
```

**Asynchronous `async with` block:**

```python
import asyncio
from GreenTrace import EmissionsTracker

async def main():
    async with EmissionsTracker(region="CN", output_file="report.csv", csv_summary_only=True):
        print("Tracking an async block...")
        await asyncio.sleep(2)
        print("Async block finished.")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Reporting

`GreenTrace` can generate reports in multiple formats. You can control this with the `output_format` and `output_file` parameters.

### HTML Report

The most visually impressive output is the HTML certificate. It's a single, self-contained file that you can easily share.

**Example (`async_report.html`):**

!HTML Report Screenshot 
*(This is a placeholder, you can replace the URL with a real screenshot of the generated `async_report.html`)*

To generate it, set the output file to have an `.html` extension:

```python
@track_emissions(output_file="my_certificate.html")
def my_function():
    # ...
```

### Other Formats

-   **JSON:** `output_file="report.json"`
-   **CSV:** `output_file="report.csv"`
-   **Console:** The default if no `output_file` is specified.

---

## Configuration

The `track_emissions` decorator and `EmissionsTracker` class accept several arguments:

-   `region` (str): The two-letter country code (e.g., "US", "DE", "CN") to use for carbon intensity data. Defaults to a global average.
-   `interval_seconds` (int): How often to take a power measurement. Default is `5`.
-   `output_file` (str): Path to save the report file. If not provided, prints to console.
-   `output_format` (str): `console`, `json`, `csv`, `html`. If an `output_file` is provided, the format is inferred from the file extension, otherwise defaults to `console`.
-   `csv_summary_only` (bool): If `True` and format is `csv`, only the summary row is saved.
-   `silent` (bool): If `True`, suppresses all console output during tracking.

## How It Works

`GreenTrace` runs a background thread (or an `asyncio.Task` in async mode) that periodically measures the power consumption of your CPU.

1.  **Power Measurement:** It uses the most accurate method available for your system. For Linux systems with Intel CPUs, it reads from the **Intel RAPL** (Running Average Power Limit) interface. For other systems, it estimates power based on current CPU utilization and the processor's TDP (Thermal Design Power).
2.  **Energy Calculation:** It integrates the power measurements over the tracking duration to calculate the total energy consumed in kilowatt-hours (kWh).
3.  **Emissions Estimation:** The total energy is multiplied by the carbon intensity factor (in gCO₂eq/kWh) for the specified geographical region to estimate the total CO₂ equivalent emissions.

## Contributing

Contributions are welcome! If you have ideas for new features, find a bug, or want to improve the documentation, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.