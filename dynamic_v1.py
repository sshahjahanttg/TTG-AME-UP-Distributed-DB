import time
import psutil
import csv
from collections import deque
from multiprocessing import Pool, cpu_count, freeze_support


# ============================================================
# CPU SMOOTHER
# Keeps a rolling average to avoid reacting to short spikes
# ============================================================
class CPUSmoother:
    def __init__(self, window_size=5):
        self.samples = deque(maxlen=window_size)

    def sample(self):
        cpu = psutil.cpu_percent(interval=0.3)
        self.samples.append(cpu)
        return self.average()

    def average(self):
        return sum(self.samples) / len(self.samples) if self.samples else 0.0


# ============================================================
# COMPUTE FUNCTION
# Represents one independent ~1-second unit of work
# ============================================================
def compute_task(n: int) -> float:
    total = 0.0
    for i in range(n):
        total += (i ** 0.5) * (i % 7)
    return total


# ============================================================
# DECISION LOGIC
# Chooses batch size based on smoothed CPU usage
# ============================================================
def decide_batch_size(current_cpu: float,
                      min_batch: int = 1,
                      max_batch: int = 10) -> int:
    if current_cpu < 40:
        return max_batch        # system idle → be aggressive
    elif current_cpu <= 75:
        return 3                # healthy operating range
    else:
        return min_batch        # system busy → slow down


# ============================================================
# DYNAMIC CONTROLLER
# ============================================================
def run_dynamic(tasks, max_cpu_fraction, csv_file):
    TOTAL_CORES = cpu_count()
    cpu_smoother = CPUSmoother(window_size=5)

    remaining_tasks = tasks.copy()
    batch_number = 1
    all_results = []

    pool = None
    current_workers = None

    while remaining_tasks:
        # ---- Measure smoothed CPU usage ----
        current_cpu = cpu_smoother.sample()

        # ---- Safety brake ----
        if current_cpu > 95:
            print(f"WARNING: CPU at {current_cpu:.1f}%, pausing 1s to avoid overload")
            time.sleep(1)
            continue

        # ---- Decide batch size ----
        batch_size = decide_batch_size(current_cpu)

        # ---- Worker count (fixed upper cap) ----
        desired_workers = max(1, int(TOTAL_CORES * max_cpu_fraction))

        # ---- Create or update worker pool ----
        if pool is None or desired_workers != current_workers:
            if pool is not None:
                pool.close()
                pool.join()
            pool = Pool(processes=desired_workers)
            current_workers = desired_workers

        # ---- Slice next batch ----
        batch = remaining_tasks[:batch_size]
        remaining_tasks = remaining_tasks[batch_size:]

        print(
            f"\nBatch {batch_number} | "
            f"CPU before: {current_cpu:.1f}% | "
            f"Batch size: {len(batch)} | "
            f"Workers: {current_workers}"
        )

        # ---- Execute batch ----
        start = time.time()
        results = pool.map(compute_task, batch)
        duration = time.time() - start

        cpu_after = cpu_smoother.sample()

        print(
            f"Batch {batch_number} completed in {duration:.2f}s | "
            f"CPU after: {cpu_after:.1f}%"
        )

        # ---- Logging to CSV ----
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                batch_number,
                len(batch),
                f"{current_cpu:.1f}",
                f"{cpu_after:.1f}",
                f"{duration:.2f}",
                current_workers
            ])

        all_results.extend(results)
        batch_number += 1

    # ---- Clean shutdown ----
    if pool is not None:
        pool.close()
        pool.join()

    return all_results


# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    freeze_support()

    TASK_SIZE = 5_000_000      # tuned to ~1 second per task
    NUM_TASKS = 1000
    MAX_CPU_FRACTION = 0.6     # safety cap on worker usage

    tasks = [TASK_SIZE] * NUM_TASKS

    CSV_FILE = f"dynamic_{NUM_TASKS}tasks.csv"

    # ---- Initialize CSV ----
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Batch_Number",
            "Batch_Size",
            "CPU_Before",
            "CPU_After",
            "Duration_Seconds",
            "Worker_Count"
        ])

    # ---- the experiment ----
    start_total = time.time()
    results = run_dynamic(tasks, MAX_CPU_FRACTION, CSV_FILE)
    end_total = time.time()

    total_time = end_total - start_total

    # ---- Logging total runtime ----
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["TOTAL", "", "", "", f"{total_time:.2f}", ""])

    print(f"\nAll {NUM_TASKS} tasks completed in {total_time:.2f} seconds")
