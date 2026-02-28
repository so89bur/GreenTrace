import sys
import os
import time
import asyncio

# Добавляем корневую директорию проекта в sys.path
# чтобы можно было импортировать carbon_py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import track_emissions


@track_emissions(interval=1, region="DE")
def process_data():
    print("Начинаем тяжелые вычисления...")
    # Симуляция работы CPU
    _ = [i * i for i in range(20_000_000)]
    time.sleep(3)
    print("Вычисления завершены.")


process_data()
