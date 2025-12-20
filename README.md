Long-Running Loop Optimization Analysis

AME-UP WIL Project – Tartigrade Ltd.
Author: Shabiba Shahjahan

Project Overview

This notebook analyzes the optimization of a long-running, CPU-bound loop using Python multiprocessing and task batching strategies. The focus is on understanding trade-offs between parallelism, task granularity, and overhead — foundational concepts relevant to distributed computation systems.

Objective

Evaluate the performance of sequential execution versus multiprocessing.

Implement and assess batching strategies to reduce inter-process communication overhead.

Draw conclusions that inform scalable design decisions for distributed workloads.

Key Experiments

Sequential Execution

Baseline performance measurement of the loop.

Observations: Linear scaling, underutilized CPU resources.

Naive Multiprocessing (no batching)

Distributes one task per worker process.

Observations: Overhead dominates in constrained environments (Colab), often slower than sequential.

Multiprocessing with Batching

Groups multiple tasks into a single batch per worker.

Results for batch sizes 5 and 10 were measured.

Observations:

Moderate batch size (5) reduced execution time.

Excessive batch size (10) reduced parallelism and increased runtime.

Demonstrates the trade-off between task granularity and resource utilization.
Excessive batch size (10) reduced parallelism and increased runtime.

Demonstrates the trade-off between task granularity and resource utilization.
