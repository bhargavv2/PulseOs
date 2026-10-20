"""
Process Manager - Operating Systems Project
Monitors system/user processes, CPU, memory, I/O counters and estimated workload type.

Run:
    python -m pip install -r requirements.txt
    python process_manager.py

Notes:
- CPU and I/O statistics vary by operating system and permissions.
- CPU-bound / I/O-bound labels are heuristic estimates, not guaranteed truths.
- This tool monitors processes; it does not terminate or modify them.
"""
import os
import time
import platform
from datetime import datetime

import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

REFRESH_SECONDS = 2.0
console = Console()
previous_io = {}
previous_cpu_time = {}
previous_sample_time = time.monotonic()


def safe_username(proc):
    try:
        return proc.username() or "Unknown"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unavailable"


def safe_name(proc):
    try:
        return proc.name() or "Unknown"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unavailable"


def process_kind(proc):
    """A practical, OS-dependent estimate of whether this is a system or user process."""
    try:
        username = proc.username()
        if username in ("root", "SYSTEM", "NT AUTHORITY\\SYSTEM"):
            return "System"
        # On Unix-like systems, many background services run as root or service accounts.
        if platform.system() in ("Linux", "Darwin") and proc.ppid() == 1:
            return "System/service"
        return "User"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def memory_mb(proc):
    try:
        return proc.memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def io_rates(proc, now):
    """Return read/write bytes per second when this OS exposes process I/O counters."""
    try:
        counters = proc.io_counters()
        current = (getattr(counters, "read_bytes", 0),
                   getattr(counters, "write_bytes", 0))
        old = previous_io.get(proc.pid)
        previous_io[proc.pid] = (current[0], current[1], now)
        if old is None:
            return None, None
        old_read, old_write, old_time = old
        elapsed = max(now - old_time, 0.001)
        return max(0, current[0] - old_read) / elapsed, max(0, current[1] - old_write) / elapsed
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess,
            AttributeError, NotImplementedError):
        return None, None


def classify_process(cpu, read_rate, write_rate):
    """
    Simple explainable heuristic:
    - CPU-bound: CPU usage >= 20% in this sample.
    - I/O-bound: CPU usage < 10% and measured read/write throughput >= 64 KiB/s.
    - Otherwise: Mixed/Unknown.
    Thresholds are project choices and should be explained in the report.
    """
    if cpu is None:
        return "Unknown"
    total_io = (read_rate or 0) + (write_rate or 0)
    if cpu >= 20.0:
        return "CPU-bound"
    if cpu < 10.0 and total_io >= 64 * 1024:
        return "I/O-bound"
    return "Mixed/Unknown"


def make_table():
    table = Table(title="Live Process Manager", expand=True, header_style="bold cyan")
    table.add_column("PID", justify="right", no_wrap=True)
    table.add_column("Process", min_width=18, max_width=30, overflow="ellipsis")
    table.add_column("Owner", min_width=10, max_width=18, overflow="ellipsis")
    table.add_column("Kind", min_width=12)
    table.add_column("CPU %", justify="right")
    table.add_column("RAM MB", justify="right")
    table.add_column("Read KB/s", justify="right")
    table.add_column("Write KB/s", justify="right")
    table.add_column("Estimate", min_width=14)
    return table


def collect_rows():
    global previous_sample_time
    now = time.monotonic()
    rows = []
    # cpu_percent(interval=None) is non-blocking; readings become useful after sampling.
    for proc in psutil.process_iter():
        try:
            with proc.oneshot():
                pid = proc.pid
                name = safe_name(proc)
                owner = safe_username(proc)
                kind = process_kind(proc)
                cpu = proc.cpu_percent(interval=None)
                mem = memory_mb(proc)
                read_rate, write_rate = io_rates(proc, now)
                estimate = classify_process(cpu, read_rate, write_rate)
                rows.append((pid, name, owner, kind, cpu, mem, read_rate, write_rate, estimate))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    previous_sample_time = now
    # Show the most CPU-active processes first.
    rows.sort(key=lambda row: row[4] if row[4] is not None else -1, reverse=True)
    return rows


def format_rate(value):
    return "N/A" if value is None else f"{value / 1024:.1f}"


def render(rows, started_at):
    table = make_table()
    for pid, name, owner, kind, cpu, mem, read_rate, write_rate, estimate in rows:
        table.add_row(
            str(pid), name, owner, kind,
            "N/A" if cpu is None else f"{cpu:.1f}",
            "N/A" if mem is None else f"{mem:.1f}",
            format_rate(read_rate), format_rate(write_rate), estimate
        )
    info = (
        f"OS: {platform.system()} {platform.release()}  |  "
        f"Logical CPUs: {psutil.cpu_count() or 'N/A'}  |  "
        f"RAM total: {psutil.virtual_memory().total / (1024**3):.2f} GB  |  "
        f"Refresh: {REFRESH_SECONDS:.0f}s  |  Started: {started_at}"
    )
    footer = Text(
        "CPU-bound / I/O-bound are heuristic estimates. N/A means unavailable or not yet sampled. "
        "Press Ctrl+C to exit.",
        style="yellow"
    )
    return Panel.fit(
        table,
        title=info,
        subtitle=footer,
        border_style="blue"
    )


def main():
    # Prime psutil's CPU sampler so the first readings are more meaningful.
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    started_at = datetime.now().strftime("%H:%M:%S")
    console.print("[bold green]Starting Process Manager...[/bold green]")
    console.print("Collecting process data. Some fields may be unavailable without permissions.")
    try:
        with Live(console=console, refresh_per_second=2, screen=True) as live:
            while True:
                rows = collect_rows()
                live.update(render(rows, started_at))
                time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        console.print("\n[bold green]Process Manager stopped safely.[/bold green]")


if __name__ == "__main__":
    main()
