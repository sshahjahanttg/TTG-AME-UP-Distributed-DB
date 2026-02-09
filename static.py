import time
import psutil
import csv
from multiprocessing import Pool, cpu_count, freeze_support

# ----- Compute function -----
def compute_task(n: int) -> float:
    total = 0.0
    for i in range(n):
        total += (i ** 0.5) * (i % 7)
    return total

# ----- Run tasks in fixed (static) batches -----
def run_batch_static(tasks, batch_size: int, max_cpu_fraction: float, csv_file: str):
    TOTAL_CORES = cpu_count()
    NUM_WORKERS = max(1, int(TOTAL_CORES * max_cpu_fraction))

    results = []

    for i in range(0, len(tasks), batch_size):
        batch_number = i // batch_size + 1
        current_batch = tasks[i:i + batch_size]

        start = time.time()
        with Pool(processes=NUM_WORKERS) as pool:
            batch_results = pool.map(compute_task, current_batch)
        duration = time.time() - start

        cpu_percent = psutil.cpu_percent(interval=0.5)

        print(
            f"Batch {batch_number} | "
            f"Batch size: {len(current_batch)} | "
            f"Time: {duration:.2f}s | "
            f"CPU after: {cpu_percent:.1f}%"
        )

        results.extend(batch_results)

        # ----- Log to CSV -----
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                batch_number,
                len(current_batch),
                duration,
                cpu_percent
            ])

    return results

# ----- Main program -----
if __name__ == "__main__":
    freeze_support()  # required on Windows

    TASK_SIZE = 5_000_000
    NUM_TASKS = 1000
    BATCH_SIZE = 5
    MAX_CPU_FRACTION = 0.5

    tasks = [TASK_SIZE] * NUM_TASKS

    CSV_FILE = f"static_{NUM_TASKS}tasks.csv"

    # ----- Initialize CSV -----
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Batch_Number",
            "Batch_Size",
            "Time_Seconds",
            "CPU_Percent"
        ])

    start_total = time.time()
    results = run_batch_static(tasks, BATCH_SIZE, MAX_CPU_FRACTION, CSV_FILE)
    end_total = time.time()

    print(f"\nAll {NUM_TASKS} tasks completed in {end_total - start_total:.2f} seconds")
