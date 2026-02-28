import sys
import os
import time
import asyncio

# Добавляем корневую директорию проекта в sys.path
# чтобы можно было импортировать carbon_py
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
    print("\nЗапуск синхронной задачи для CSV отчета ...")
    time.sleep(20)
    print("Синхронная задача завершена.")


short_sync_task()
