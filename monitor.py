#!/usr/bin/env python3
"""CPU and memory usage monitor — samples for 10 seconds then prints a summary."""

import psutil
import time
from datetime import datetime

SAMPLE_INTERVAL = 1   # seconds between samples
SAMPLE_COUNT    = 10  # total samples to collect

cpu_samples    = []
mem_samples    = []
swap_samples   = []

print(f"Collecting {SAMPLE_COUNT} samples (one per second)...\n")
print(f"{'#':<4} {'CPU %':>6}  {'Mem %':>6}  {'Mem Used':>10}  {'Swap %':>6}")
print("-" * 42)

for i in range(SAMPLE_COUNT):
    cpu  = psutil.cpu_percent(interval=SAMPLE_INTERVAL)
    mem  = psutil.virtual_memory()
    swap = psutil.swap_memory()

    cpu_samples.append(cpu)
    mem_samples.append(mem.percent)
    swap_samples.append(swap.percent)

    used_gb = mem.used / (1024 ** 3)
    print(f"{i+1:<4} {cpu:>6.1f}%  {mem.percent:>6.1f}%  {used_gb:>8.2f}GB  {swap.percent:>6.1f}%")

# ── Summary ──────────────────────────────────────────────────────────────────
mem_info  = psutil.virtual_memory()
swap_info = psutil.swap_memory()
cpu_count = psutil.cpu_count(logical=True)
cpu_freq  = psutil.cpu_freq()

total_ram_gb  = mem_info.total  / (1024 ** 3)
avail_ram_gb  = mem_info.available / (1024 ** 3)
total_swap_gb = swap_info.total / (1024 ** 3)

print("\n" + "=" * 50)
print(f"  SUMMARY  —  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

print("\n[CPU]")
print(f"  Logical cores : {cpu_count}")
if cpu_freq:
    print(f"  Current freq  : {cpu_freq.current:.0f} MHz  (max {cpu_freq.max:.0f} MHz)")
print(f"  Avg usage     : {sum(cpu_samples)/len(cpu_samples):.1f}%")
print(f"  Peak usage    : {max(cpu_samples):.1f}%")
print(f"  Min usage     : {min(cpu_samples):.1f}%")

print("\n[Memory]")
print(f"  Total RAM     : {total_ram_gb:.2f} GB")
print(f"  Available     : {avail_ram_gb:.2f} GB")
print(f"  Avg used      : {sum(mem_samples)/len(mem_samples):.1f}%")
print(f"  Peak used     : {max(mem_samples):.1f}%")

print("\n[Swap]")
print(f"  Total swap    : {total_swap_gb:.2f} GB")
print(f"  Avg used      : {sum(swap_samples)/len(swap_samples):.1f}%")
print(f"  Peak used     : {max(swap_samples):.1f}%")

# Per-core breakdown
per_core = psutil.cpu_percent(percpu=True)
print("\n[Per-Core CPU %]")
for idx, pct in enumerate(per_core):
    bar = "█" * int(pct / 5)
    print(f"  Core {idx:<2}  {pct:>5.1f}%  {bar}")

print()
