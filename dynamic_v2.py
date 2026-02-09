import time
import psutil
import csv
from collections import deque
from multiprocessing import Pool, cpu_count, freeze_support


class CPUSmoother:
    def __init__(self, window_size=5):
        self.samples = deque(maxlen=window_size)

    def sample(self):
        cpu = psutil.cpu_percent(interval=None)  # NON-blocking
        self.samples.append(cpu)
        return self.average()

    def average(self):
        return sum(self.samples) / len(self.samples) if self.samples else 0.0


def compute_task(n: int) -> float:
    total = 0.0
    for i in range(n):
        total += (i ** 0.5) * (i % 7)
    return total


def decide_batch_size(cpu):
    if cpu < 40:
        return 20
    elif cpu < 70:
        return 10
    else:
        return 2


def run_dynamic(tasks, max_cpu_fraction, csv_file):
    TOTAL_CORES = cpu_count()
    workers = max(1, int(TOTAL_CORES * max_cpu_fraction))

    cpu_smoother = CPUSmoother()
    pool = Pool(processes=workers)

    batch_number = 1
    index = 0
    results = []

    while index < len(tasks):
        cpu_now = cpu_smoother.sample()
        batch_size = decide_batch_size(cpu_now)

        batch = tasks[index:index + batch_size]
        index += batch_size

        start = time.time()
        batch_results = pool.map(compute_task, batch)
        duration = time.time() - start

        cpu_after = cpu_smoother.sample()

        print(
            f"Batch {batch_number} | "
            f"CPU before: {cpu_now:.1f}% | "
            f"Batch size: {len(batch)} | "
            f"Duration: {duration:.2f}s"
        )

        with open(csv_file, "a", newline="") as f:
            csv.writer(f).writerow([
                batch_number,
                len(batch),
                f"{cpu_now:.1f}",
                f"{cpu_after:.1f}",
                f"{duration:.2f}",
                workers
            ])

        results.extend(batch_results)
        batch_number += 1

    pool.close()
    pool.join()
    return results


if __name__ == "__main__":
    freeze_support()

    TASK_SIZE = 5_000_000
    NUM_TASKS = 1000
    MAX_CPU_FRACTION = 0.9

    tasks = [TASK_SIZE] * NUM_TASKS
    CSV_FILE = "dynamic_improved.csv"

    with open(CSV_FILE, "w", newline="") as f:
        csv.writer(f).writerow([
            "Batch",
            "Batch_Size",
            "CPU_Before",
            "CPU_After",
            "Duration",
            "Workers"
        ])

    start = time.time()
    run_dynamic(tasks, MAX_CPU_FRACTION, CSV_FILE)
    end = time.time()

    print(f"\nAll tasks completed in {end - start:.2f} seconds")
