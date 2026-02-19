**Dynamic CPU-Aware Task Scheduling in Python**

**Overview:** This project explores different strategies for optimizing a long-running, CPU-bound workload using Python multiprocessing.

**The objective was to:**
Reduce total execution time
Maintain controlled CPU usage
Compare static vs dynamic scheduling strategies
Avoid fully saturating system resources

Three execution strategies were implemented and benchmarked.

**Problem Statement**
The workload consists of many independent CPU-bound tasks (~1 second per task).
Since tasks are independent, they can be parallelized using multiprocessing.

The challenge was not only to speed up execution, but to do so in a controlled and scalable way, avoiding excessive CPU saturation.

**Implemented Approaches**

**1. Static Batching (static.py)**

Fixed batch size:
Fixed number of worker processes
No CPU monitoring
Predictable but not adaptive

Characteristics:
Stable behavior
Underutilizes available CPU
Baseline for comparison

**2. Dynamic Scheduling – Version 1 (dynamic_v1.py)**

Adjusts batch size based on real-time CPU usage
Reacts immediately to CPU changes

Observed Issues:
CPU readings fluctuate naturally
Algorithm overreacted to short-term spikes
Frequent batch size changes
High scheduling overhead
Worse performance than the static baseline

**3. Dynamic Scheduling – Version 2 (dynamic_v2.py)**

Improved version with stability-focused refinements:
CPU usage smoothing (averaged readings)
Larger maximum batch size (reduced overhead)
Increased minimum batch size (avoids inefficient micro-batches)
Controlled CPU cap (80% maximum usage)
Gradual scaling adjustments instead of reactive shifts

Results:
Stable batch sizes
Sustained CPU utilization
Significant runtime improvement
Outperforms both static and dynamic_v1

**Performance Comparison (1000 Tasks)**

Static Version
Total Runtime: 296 seconds
Average CPU Usage: ~7%
Average Batch Size: 5 tasks

Verdict: Stable baseline, but underutilizes hardware

Dynamic Version 1 (Naive reactive)
Total Runtime: 572 seconds
Average CPU Usage: ~9%
Average Batch Size: ~10 tasks (highly unstable)

Verdict: Actually 93% slower than static! Over-reaction to CPU spikes caused chaos

Dynamic Version 2 (Improved smooth control)
Total Runtime: 180–260 seconds (depending on CPU cap setting)
Average CPU Usage: 50–80%
Average Batch Size: 18–20 tasks (stable)

Verdict: 12-39% faster than static, good system citizenship



* Runtime varies depending on CPU cap configuration and system load.

**Key Insights**

Naive dynamic scaling can reduce performance if it reacts to noisy CPU signals.
Larger, stable batches reduce scheduling overhead.
Smoothing feedback signals significantly improves control stability.
Performance gains were primarily due to improved scheduling logic, not just increased CPU usage.
Controlled CPU caps allow coexistence with other system processes while maintaining strong throughput.

**How to Run**

Install dependencies:
pip install psutil


Run static baseline:
python static.py


Run first dynamic attempt:
python dynamic_v1.py


Run improved dynamic version:
python dynamic_v2.py


***Optional: Modify MAX_CPU_FRACTION inside dynamic_v2.py to experiment with different CPU limits.


**Logging and Benchmarking**

Each dynamic run logs:
Batch number
Batch size
CPU usage before and after execution
Batch duration

This allows benchmarking and visualization of:
CPU stability
Batch scaling behavior
Throughput efficiency


**Future Improvements**

Potential next steps include:
Adaptive CPU target based on idle system detection
Predictive scaling rather than reactive scaling
Extended benchmarking at larger workloads (10k+ tasks)
Visualization dashboards for performance analysis

**Conclusion**

This project demonstrates that effective dynamic scheduling requires stability and thoughtful control logic.
Simply reacting to CPU usage is insufficient — smoothing, batching strategy, and scaling discipline are essential for achieving real performance gains.
