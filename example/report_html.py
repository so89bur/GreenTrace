import sys
import os
import time
import asyncio

# Добавляем корневую директорию проекта в sys.path
# чтобы можно было импортировать carbon_py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import track_emissions


@track_emissions(interval=1, region="FR", output_file="async_report.html")
async def async_process_data():
    print("Начинаем асинхронные вычисления...")
    await asyncio.sleep(10)
    print("Вычисления завершены.")


asyncio.run(async_process_data())
