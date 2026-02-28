import sys
import os
import time
import asyncio
import threading

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carbonPy.tracker import EmissionsTracker, track_emissions, TrackerNotRunningError


@track_emissions(interval=1, region="FR", name="long_task")
def long_running_task():
    """Длительная задача, за которой мы будем наблюдать."""
    print("Начинаем длительные вычисления...")
    time.sleep(15)
    print("Длительные вычисления завершены.")


def monitor_task():
    """Функция для мониторинга, запрашивает данные каждые 3 секунды."""
    print("\n--- Мониторинг запущен ---")
    while True:
        try:
            # Получаем активный трекер по его имени
            tracker = EmissionsTracker.get_active_tracker("long_task")
            data = tracker.get_current_data()
            emissions = data["summary"]["emissions_gco2eq"]
            duration = data["summary"]["duration_seconds"]
            print(
                f"Промежуточный результат: {emissions:.4f} гCO₂экв за {duration:.2f} сек."
            )
            time.sleep(3)
        except TrackerNotRunningError:
            print("--- Мониторинг завершен (трекер остановлен) ---\n")
            break


# Запускаем задачу для мониторинга в отдельном потоке
monitor_thread = threading.Thread(target=monitor_task)
monitor_thread.start()

# Запускаем основную длительную задачу
long_running_task()

# Ожидаем завершения потока мониторинга
monitor_thread.join()
