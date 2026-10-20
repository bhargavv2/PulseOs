import os
import time
import signal
import platform
from datetime import datetime

import pandas as pd
import psutil
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="PulseOS · Kernel Process Cockpit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Modern, human-crafted CSS with Dark/Light adaptive design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1650px;
    }

    /* Cockpit Header Card */
    .cockpit-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.65) 100%);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }

    .cockpit-title-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }

    .brand-title {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #3b82f6, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-name {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .brand-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-left: 6px;
        vertical-align: middle;
    }

    .brand-sub {
        margin: 4px 0 0 0;
        font-size: 0.86rem;
        opacity: 0.75;
    }

    /* Live Telemetry Beacon */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .status-live {
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-paused {
        background: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    @keyframes live-pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .beacon-dot-live {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        animation: live-pulse 2s infinite;
    }

    .beacon-dot-paused {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #f59e0b;
    }

    /* System metadata strip */
    .sys-meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid rgba(148, 163, 184, 0.12);
    }

    .meta-item {
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .meta-label {
        font-weight: 600;
        opacity: 0.55;
        letter-spacing: 0.05em;
        font-size: 0.72rem;
    }

    .meta-val {
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* KPI Summary Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 1.25rem;
    }

    .kpi-card {
        background: var(--secondary-background-color, rgba(148, 163, 184, 0.05));
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
        transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.35);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }

    .kpi-blue::before { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
    .kpi-emerald::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .kpi-amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .kpi-purple::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
    .kpi-rose::before { background: linear-gradient(90deg, #f43f5e, #fb7185); }

    .kpi-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.65;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.15;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 5px;
    }

    .kpi-sub {
        font-size: 0.76rem;
        opacity: 0.72;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Badges & Pills */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    .badge-cpu { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-io { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }
    .badge-balanced { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-mixed { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* Top Consumer Card */
    .top-consumer-card {
        background: var(--secondary-background-color, rgba(148, 163, 184, 0.04));
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 1rem;
    }

    .consumer-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.08);
        font-size: 0.84rem;
    }
    .consumer-item:last-child { border-bottom: none; }

    .consumer-name {
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 65%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .consumer-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }

    /* Inspector Card */
    .inspector-box {
        background: var(--secondary-background-color, rgba(148, 163, 184, 0.05));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 20px;
        margin-top: 1rem;
    }

    .inspector-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    }

    .code-chip {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(148, 163, 184, 0.12);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        word-break: break-all;
    }

    /* Streamlit overrides */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# STATE INITIALIZATION
# ==========================================
if "io_previous" not in st.session_state:
    st.session_state.io_previous = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_pid" not in st.session_state:
    st.session_state.selected_pid = None
if "refresh_paused" not in st.session_state:
    st.session_state.refresh_paused = False
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 2
if "prev_sys_io" not in st.session_state:
    st.session_state.prev_sys_io = {
        "time": time.monotonic(),
        "disk": psutil.disk_io_counters(),
        "net": psutil.net_io_counters(),
    }
if "last_cpu_prime" not in st.session_state:
    # Prime non-blocking counters on cold start
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    st.session_state.last_cpu_prime = True


# ==========================================
# SYSTEM & PROCESS DATA HELPERS
# ==========================================
def get_system_metadata():
    """Retrieve host hardware specifications, kernel release, and uptime."""
    boot_timestamp = psutil.boot_time()
    uptime_seconds = max(0, time.time() - boot_timestamp)
    days, rem = divmod(int(uptime_seconds), 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    
    uptime_parts = []
    if days > 0: uptime_parts.append(f"{days}d")
    if hours > 0 or days > 0: uptime_parts.append(f"{hours}h")
    uptime_parts.append(f"{minutes}m")
    uptime_str = " ".join(uptime_parts) if uptime_parts else "<1m"

    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)

    return {
        "host": platform.node() or "localhost",
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.machine(),
        "uptime": uptime_str,
        "cores_physical": psutil.cpu_count(logical=False) or 1,
        "cores_logical": psutil.cpu_count(logical=True) or 1,
        "load_avg": f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
    }


def classify_workload(cpu, read_bps, write_bps, cpu_threshold=20.0, io_kb_threshold=64.0, io_cpu_max=10.0):
    """
    Transparent OS Project Workload Classifier:
    - CPU-bound: Process CPU usage >= cpu_threshold% (default 20%).
    - I/O-bound: Process CPU usage < io_cpu_max% (default 10%) and observed disk I/O >= io_kb_threshold KB/s.
    - Balanced / Idle: Normal activity within balanced boundaries.
    - Mixed / Unknown: I/O telemetry unavailable (e.g. unprivileged user space on macOS) or neither rule triggered.
    """
    if cpu is None:
        return "Unknown"
    io_total = (read_bps or 0) + (write_bps or 0)
    if cpu >= cpu_threshold:
        return "CPU-bound"
    if read_bps is not None or write_bps is not None:
        if cpu < io_cpu_max and io_total >= io_kb_threshold * 1024:
            return "I/O-bound"
        return "Balanced"
    else:
        # Per-process I/O unsupported or unprivileged on current OS
        if cpu >= cpu_threshold:
            return "CPU-bound"
        if cpu < 1.0:
            return "Idle / Low CPU"
        return "Active (I/O unavail)"


def infer_process_kind(proc, username):
    """Approximation of system vs user process based on account privileges and parent hierarchy."""
    try:
        if username in ("root", "SYSTEM", "NT AUTHORITY\\SYSTEM", "_coreaudiod", "_windowserver"):
            return "System"
        if platform.system() in ("Linux", "Darwin") and proc.ppid() == 1:
            return "Service"
        return "User"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"


def compute_system_io_throughput():
    """Calculate system-wide disk and network throughput (KB/s)."""
    now = time.monotonic()
    prev = st.session_state.prev_sys_io
    dt = max(now - prev["time"], 0.001)

    cur_disk = psutil.disk_io_counters()
    cur_net = psutil.net_io_counters()

    disk_read_kbs = 0.0
    disk_write_kbs = 0.0
    if cur_disk and prev["disk"]:
        disk_read_kbs = max(0, cur_disk.read_bytes - prev["disk"].read_bytes) / dt / 1024
        disk_write_kbs = max(0, cur_disk.write_bytes - prev["disk"].write_bytes) / dt / 1024

    net_down_kbs = 0.0
    net_up_kbs = 0.0
    if cur_net and prev["net"]:
        net_down_kbs = max(0, cur_net.bytes_recv - prev["net"].bytes_recv) / dt / 1024
        net_up_kbs = max(0, cur_net.bytes_sent - prev["net"].bytes_sent) / dt / 1024

    st.session_state.prev_sys_io = {
        "time": now,
        "disk": cur_disk,
        "net": cur_net,
    }

    return {
        "disk_read_kbs": disk_read_kbs,
        "disk_write_kbs": disk_write_kbs,
        "net_down_kbs": net_down_kbs,
        "net_up_kbs": net_up_kbs,
    }


def collect_processes(cpu_threshold=20.0, io_kb_threshold=64.0, io_cpu_max=10.0):
    """Enumerate all active OS processes with resource metrics and differential I/O throughput."""
    now = time.monotonic()
    rows = []
    previous = st.session_state.io_previous
    alive_pids = set()

    for proc in psutil.process_iter():
        try:
            with proc.oneshot():
                pid = proc.pid
                alive_pids.add(pid)
                name = proc.name() or "Unknown"
                
                try:
                    username = proc.username() or "Unknown"
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    username = "Restricted"

                cpu = proc.cpu_percent(interval=None)
                
                try:
                    mem_info = proc.memory_info()
                    rss_mb = mem_info.rss / (1024 * 1024)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    rss_mb = 0.0

                try:
                    mem_pct = proc.memory_percent()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    mem_pct = 0.0

                try:
                    status = proc.status()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    status = "unknown"

                try:
                    threads = proc.num_threads()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    threads = 1

                # Differential per-process disk I/O calculation
                read_bps = write_bps = None
                try:
                    io = proc.io_counters()
                    current_read = getattr(io, "read_bytes", None)
                    current_write = getattr(io, "write_bytes", None)
                    old = previous.get(pid)
                    if old and current_read is not None and current_write is not None:
                        old_read, old_write, old_time = old
                        elapsed = max(now - old_time, 0.001)
                        read_bps = max(0, current_read - old_read) / elapsed
                        write_bps = max(0, current_write - old_write) / elapsed
                    if current_read is not None and current_write is not None:
                        previous[pid] = (current_read, current_write, now)
                except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError, NotImplementedError):
                    pass

                estimate = classify_workload(cpu, read_bps, write_bps, cpu_threshold, io_kb_threshold, io_cpu_max)

                rows.append({
                    "PID": pid,
                    "Process": name,
                    "Owner": username,
                    "Kind": infer_process_kind(proc, username),
                    "Status": status,
                    "CPU %": round(cpu, 1),
                    "RAM MB": round(rss_mb, 1),
                    "RAM %": round(mem_pct, 1),
                    "Threads": threads,
                    "Read KB/s": None if read_bps is None else round(read_bps / 1024, 1),
                    "Write KB/s": None if write_bps is None else round(write_bps / 1024, 1),
                    "Estimate": estimate,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Clean up terminated PIDs from the state dictionary
    for pid in list(previous.keys()):
        if pid not in alive_pids:
            previous.pop(pid, None)

    return pd.DataFrame(rows)


def inspect_single_process(pid):
    """Deep-dive diagnostic inspection of a specific PID."""
    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            name = proc.name()
            status = proc.status()
            create_time = datetime.fromtimestamp(proc.create_time()).strftime("%Y-%m-%d %H:%M:%S")
            uptime_sec = max(0, time.time() - proc.create_time())
            m, s = divmod(int(uptime_sec), 60)
            h, m = divmod(m, 60)
            uptime_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"
            
            try: username = proc.username()
            except Exception: username = "Unavailable"
            
            try: ppid = proc.ppid()
            except Exception: ppid = "N/A"
            
            try: parent_name = proc.parent().name() if proc.parent() else "None"
            except Exception: parent_name = "Unavailable"

            try: exe_path = proc.exe()
            except Exception: exe_path = "Unavailable (Permissions or Kernel process)"

            try: cwd = proc.cwd()
            except Exception: cwd = "Unavailable"

            try: cmdline = " ".join(proc.cmdline())
            except Exception: cmdline = "Unavailable"

            try: cpu_times = proc.cpu_times()
            except Exception: cpu_times = None

            try: mem_info = proc.memory_info()
            except Exception: mem_info = None

            try: threads = proc.num_threads()
            except Exception: threads = "Unavailable"

            try: nice = proc.nice()
            except Exception: nice = "N/A"

            try: num_fds = proc.num_fds()
            except Exception: num_fds = "N/A"

            return {
                "pid": pid,
                "name": name,
                "ppid": ppid,
                "parent_name": parent_name,
                "status": status,
                "username": username,
                "create_time": create_time,
                "uptime": uptime_str,
                "exe": exe_path,
                "cwd": cwd,
                "cmdline": cmdline or name,
                "cpu_percent": proc.cpu_percent(interval=None),
                "cpu_user": f"{cpu_times.user:.2f}s" if cpu_times else "N/A",
                "cpu_system": f"{cpu_times.system:.2f}s" if cpu_times else "N/A",
                "rss_mb": round(mem_info.rss / (1024*1024), 2) if mem_info else "N/A",
                "vms_mb": round(mem_info.vms / (1024*1024), 2) if mem_info else "N/A",
                "mem_percent": round(proc.memory_percent(), 2) if hasattr(proc, "memory_percent") else "N/A",
                "threads": threads,
                "nice": nice,
                "num_fds": num_fds,
            }
    except psutil.NoSuchProcess:
        return {"error": f"Process PID {pid} has terminated or does not exist."}
    except psutil.AccessDenied:
        return {"error": f"Access Denied: OS permissions restrict inspecting PID {pid}."}
    except Exception as e:
        return {"error": f"Diagnostic error inspecting PID {pid}: {str(e)}"}


def dispatch_process_signal(pid: int, sig_name: str):
    """Safely send signals with strict kernel & self guards."""
    if pid <= 1:
        return False, "Kernel Guard: PID 0 and PID 1 are protected system anchors and cannot be terminated."
    if pid == os.getpid():
        return False, "Self Guard: Terminating the active Streamlit telemetry engine is blocked."
    
    try:
        p = psutil.Process(pid)
        proc_name = p.name()
        if sig_name == "TERM":
            p.terminate()
            return True, f"Sent SIGTERM (Graceful Terminate) to '{proc_name}' (PID {pid})."
        elif sig_name == "KILL":
            p.kill()
            return True, f"Sent SIGKILL (Force Kill) to '{proc_name}' (PID {pid})."
        return False, f"Unsupported signal type: {sig_name}"
    except psutil.NoSuchProcess:
        return False, f"Process PID {pid} no longer exists."
    except psutil.AccessDenied:
        return False, f"Permission Denied: Root / administrator privileges required to terminate PID {pid}."
    except Exception as e:
        return False, f"Signal error: {str(e)}"


# ==========================================
# CONFIRMATION MODAL DIALOG
# ==========================================
@st.dialog("⚠️ Process Termination Guard")
def signal_confirmation_modal(pid: int, proc_name: str, sig_type: str):
    st.markdown(f"""
    You are about to issue an OS signal to an active process:
    - **Target Process:** `{proc_name}`
    - **Process ID (PID):** `{pid}`
    - **Signal:** `SIG{sig_type}` ({'Graceful Request' if sig_type == 'TERM' else 'Immediate Hard Kill'})
    """)
    
    if sig_type == "KILL":
        st.warning("⚠️ **SIGKILL** bypasses process signal handlers. All unsaved state in the target process will be terminated instantly.")
    else:
        st.info("ℹ️ **SIGTERM** gives the target process an opportunity to flush buffers and release lockfiles cleanly.")

    confirmed = st.checkbox("I acknowledge the operational impact and wish to proceed.", value=False)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"Confirm & Send SIG{sig_type}", type="primary", disabled=not confirmed, use_container_width=True):
            success, msg = dispatch_process_signal(pid, sig_type)
            if success:
                st.success(msg)
                time.sleep(1.2)
                st.rerun()
            else:
                st.error(msg)
    with col2:
        if st.button("Cancel & Return", use_container_width=True):
            st.rerun()


# ==========================================
# SIDEBAR CONTROLS & HARDWARE SPECS
# ==========================================
meta = get_system_metadata()

with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    auto_refresh = st.toggle("⚡ Live Telemetry Stream", value=not st.session_state.refresh_paused)
    st.session_state.refresh_paused = not auto_refresh

    refresh_interval = st.select_slider(
        "Sampling Interval",
        options=[1, 2, 5, 10, 30],
        value=st.session_state.refresh_interval,
        format_func=lambda x: f"{x}s",
    )
    st.session_state.refresh_interval = refresh_interval

    if st.button("🔄 Trigger Single Refresh", use_container_width=True):
        st.rerun()

    if st.button("🧹 Clear Trend Buffer", use_container_width=True):
        st.session_state.history = []
        st.success("Buffer reset.")

    st.divider()

    with st.expander("🛠️ Heuristic Threshold Tuning", expanded=False):
        st.caption("Adjust the transparent project classification rules in real time:")
        thresh_cpu = st.slider("CPU-bound threshold (%)", 10.0, 50.0, 20.0, step=2.0)
        thresh_io = st.slider("I/O-bound threshold (KB/s)", 16.0, 512.0, 64.0, step=16.0)
        thresh_io_max_cpu = st.slider("Max CPU for I/O bound (%)", 2.0, 25.0, 10.0, step=1.0)

    st.divider()

    st.markdown("### 🖥️ Hardware Telemetry")
    st.markdown(f"""
    - **Host Node:** `{meta['host']}`
    - **Kernel:** `{meta['os']}`
    - **Architecture:** `{meta['arch']}`
    - **Logical Threads:** `{meta['cores_logical']}`
    - **Physical Cores:** `{meta['cores_physical']}`
    - **System Uptime:** `{meta['uptime']}`
    - **Load Average:** `{meta['load_avg']}`
    """)
    st.caption("PulseOS Engine v2.4 · Multi-Platform Kernel Profiler")


# ==========================================
# MAIN DASHBOARD FRAGMENT
# ==========================================
# Run interval is None when paused, giving the user a rock-solid freeze state to inspect rows without jitter.
run_interval = None if st.session_state.refresh_paused else st.session_state.refresh_interval

@st.fragment(run_every=run_interval)
def render_cockpit():
    # Collect live dataset
    t0 = time.monotonic()
    df = collect_processes(
        cpu_threshold=thresh_cpu if 'thresh_cpu' in globals() else 20.0,
        io_kb_threshold=thresh_io if 'thresh_io' in globals() else 64.0,
        io_cpu_max=thresh_io_max_cpu if 'thresh_io_max_cpu' in globals() else 10.0,
    )
    collect_latency_ms = (time.monotonic() - t0) * 1000

    # System-wide metrics
    cpu_overall = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    per_cpu = psutil.cpu_percent(interval=None, percpu=True)
    io_rates = compute_system_io_throughput()

    # Time series history buffer (up to 60 samples)
    st.session_state.history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "CPU %": float(cpu_overall),
        "RAM %": float(mem.percent),
        "Swap %": float(swap.percent),
    })
    st.session_state.history = st.session_state.history[-60:]

    total_procs = len(df)
    running_procs = int((df["Status"] == "running").sum()) if not df.empty else 0
    sleeping_procs = int((df["Status"].isin(["sleeping", "idle"])).sum()) if not df.empty else 0
    cpu_bound_count = int((df["Estimate"] == "CPU-bound").sum()) if not df.empty else 0
    io_bound_count = int((df["Estimate"] == "I/O-bound").sum()) if not df.empty else 0
    balanced_count = total_procs - cpu_bound_count - io_bound_count

    # Header Card
    status_class = "status-paused" if st.session_state.refresh_paused else "status-live"
    dot_class = "beacon-dot-paused" if st.session_state.refresh_paused else "beacon-dot-live"
    status_label = "Telemetry Paused" if st.session_state.refresh_paused else f"Live Stream ({st.session_state.refresh_interval}s)"

    st.markdown(f"""
    <div class="cockpit-header">
        <div class="cockpit-title-row">
            <div class="brand-title">
                <span class="brand-icon">⚡</span>
                <div>
                    <h1 class="brand-name">PulseOS <span class="brand-badge">Process Cockpit</span></h1>
                    <p class="brand-sub">Real-time kernel telemetry, resource allocation analytics & heuristic diagnostics</p>
                </div>
            </div>
            <div class="status-badge {status_class}">
                <span class="{dot_class}"></span>
                <span>{status_label}</span>
            </div>
        </div>
        <div class="sys-meta-strip">
            <div class="meta-item"><span class="meta-label">HOST</span> <span class="meta-val">{meta['host']}</span></div>
            <div class="meta-item"><span class="meta-label">OS KERNEL</span> <span class="meta-val">{meta['os']} ({meta['arch']})</span></div>
            <div class="meta-item"><span class="meta-label">UPTIME</span> <span class="meta-val">{meta['uptime']}</span></div>
            <div class="meta-item"><span class="meta-label">CORES</span> <span class="meta-val">{meta['cores_physical']} Phys / {meta['cores_logical']} Log</span></div>
            <div class="meta-item"><span class="meta-label">PHYSICAL RAM</span> <span class="meta-val">{mem.total / (1024**3):.1f} GB</span></div>
            <div class="meta-item"><span class="meta-label">POLL SPEED</span> <span class="meta-val">{collect_latency_ms:.0f} ms</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5-Column Executive KPI Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-blue">
            <div class="kpi-label">Active Processes</div>
            <div class="kpi-value">{total_procs:,}</div>
            <div class="kpi-sub"><b>{running_procs}</b> Running · <b>{sleeping_procs}</b> Sleeping</div>
        </div>
        <div class="kpi-card kpi-emerald">
            <div class="kpi-label">Overall CPU Load</div>
            <div class="kpi-value">{cpu_overall:.1f}%</div>
            <div class="kpi-sub">Load Avg: <b>{meta['load_avg']}</b></div>
        </div>
        <div class="kpi-card kpi-amber">
            <div class="kpi-label">Physical RAM in Use</div>
            <div class="kpi-value">{mem.percent:.1f}%</div>
            <div class="kpi-sub">{mem.used / (1024**3):.2f} / {mem.total / (1024**3):.2f} GB · {mem.available / (1024**3):.2f} GB Free</div>
        </div>
        <div class="kpi-card kpi-purple">
            <div class="kpi-label">Swap / Virtual</div>
            <div class="kpi-value">{swap.percent:.1f}%</div>
            <div class="kpi-sub">{swap.used / (1024**3):.2f} / {swap.total / (1024**3):.2f} GB Allocated</div>
        </div>
        <div class="kpi-card kpi-rose">
            <div class="kpi-label">Workload Estimates</div>
            <div class="kpi-value">🔥 {cpu_bound_count} <span style="font-size:1.1rem;font-weight:500;opacity:0.6;">CPU</span> · 💾 {io_bound_count} <span style="font-size:1.1rem;font-weight:500;opacity:0.6;">I/O</span></div>
            <div class="kpi-sub">{balanced_count} Balanced / Background Tasks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # TABS NAVIGATION
    # ==========================================
    tab_explorer, tab_charts, tab_inspector, tab_docs = st.tabs([
        "🖥️ Process Explorer",
        "📈 System Telemetry & Performance",
        "🔍 Deep-Dive Process Inspector",
        "📘 OS Architecture & Heuristics",
    ])

    # ------------------------------------------
    # TAB 1: PROCESS EXPLORER
    # ------------------------------------------
    with tab_explorer:
        # Quick filter pills
        pill_selection = st.pills(
            "Quick Filter Preset",
            ["All Processes", "User Apps", "System Services", "High CPU (>10%)", "High RAM (>250MB)", "🔥 CPU-bound", "💾 I/O-bound"],
            default="All Processes",
            label_visibility="collapsed",
        )

        f_col1, f_col2, f_col3 = st.columns([2.5, 1.2, 0.9])
        with f_col1:
            search_query = st.text_input(
                "Filter by keyword",
                placeholder="Search by Process name, PID, or User account…",
                label_visibility="collapsed",
            )
        with f_col2:
            sort_field = st.selectbox(
                "Sort Table By",
                ["CPU %", "RAM MB", "Process", "PID", "Threads", "Read KB/s", "Write KB/s"],
                index=0,
                label_visibility="collapsed",
            )
        with f_col3:
            sort_desc = st.toggle("Descending", value=True)

        # Apply filtering logic
        filtered_df = df.copy()
        
        # Pill preset filtering
        if pill_selection == "User Apps":
            filtered_df = filtered_df[filtered_df["Kind"] == "User"]
        elif pill_selection == "System Services":
            filtered_df = filtered_df[filtered_df["Kind"].isin(["System", "Service"])]
        elif pill_selection == "High CPU (>10%)":
            filtered_df = filtered_df[filtered_df["CPU %"] >= 10.0]
        elif pill_selection == "High RAM (>250MB)":
            filtered_df = filtered_df[filtered_df["RAM MB"] >= 250.0]
        elif pill_selection == "🔥 CPU-bound":
            filtered_df = filtered_df[filtered_df["Estimate"] == "CPU-bound"]
        elif pill_selection == "💾 I/O-bound":
            filtered_df = filtered_df[filtered_df["Estimate"] == "I/O-bound"]

        # Search box filtering
        if search_query.strip():
            sq = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["Process"].astype(str).str.lower().str.contains(sq, na=False)
                | filtered_df["Owner"].astype(str).str.lower().str.contains(sq, na=False)
                | filtered_df["PID"].astype(str).str.contains(sq, na=False)
            ]

        # Sorting
        filtered_df = filtered_df.sort_values(by=sort_field, ascending=not sort_desc, na_position="last")

        # Top 5 Consumers Glance (Expandable / Side-by-side)
        with st.expander("⚡ Top Resource Consumers Glance (CPU & Memory Leaders)", expanded=False):
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("**🔥 Top 5 CPU Consumers**")
                top_cpu = df.nlargest(5, "CPU %")
                for _, row in top_cpu.iterrows():
                    pct = row['CPU %']
                    bar_w = min(100, int(pct))
                    st.markdown(f"""
                    <div class="consumer-item">
                        <span class="consumer-name"><b>{row['Process']}</b> <span style="opacity:.6;font-size:.78rem;">(PID {row['PID']})</span></span>
                        <span class="consumer-val" style="color: {'#ef4444' if pct > 30 else '#f59e0b'};">{pct:.1f}% CPU</span>
                    </div>
                    """, unsafe_allow_html=True)
            with c_right:
                st.markdown("**💾 Top 5 Memory Consumers**")
                top_mem = df.nlargest(5, "RAM MB")
                for _, row in top_mem.iterrows():
                    mb = row['RAM MB']
                    st.markdown(f"""
                    <div class="consumer-item">
                        <span class="consumer-name"><b>{row['Process']}</b> <span style="opacity:.6;font-size:.78rem;">(PID {row['PID']})</span></span>
                        <span class="consumer-val" style="color: {'#8b5cf6' if mb > 1024 else '#3b82f6'};">{mb:.1f} MB</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Interactive Table with Selection
        st.markdown(f"<p style='font-size:0.84rem;opacity:0.75;margin:8px 0;'>Showing <b>{len(filtered_df):,}</b> of {len(df):,} processes · Click any row to inspect process details</p>", unsafe_allow_html=True)

        selection = st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=440,
            selection_mode="single-row",
            on_select="rerun",
            column_config={
                "PID": st.column_config.NumberColumn("PID", format="%d"),
                "Process": st.column_config.TextColumn("Process Name"),
                "Owner": st.column_config.TextColumn("Owner"),
                "Kind": st.column_config.TextColumn("Type"),
                "Status": st.column_config.TextColumn("Status"),
                "CPU %": st.column_config.ProgressColumn("CPU %", min_value=0, max_value=100, format="%.1f%%"),
                "RAM MB": st.column_config.NumberColumn("RAM MB", format="%.1f MB"),
                "RAM %": st.column_config.ProgressColumn("RAM %", min_value=0, max_value=100, format="%.1f%%"),
                "Threads": st.column_config.NumberColumn("Threads", format="%d"),
                "Read KB/s": st.column_config.NumberColumn("Read KB/s", format="%.1f"),
                "Write KB/s": st.column_config.NumberColumn("Write KB/s", format="%.1f"),
                "Estimate": st.column_config.TextColumn("Workload Tag"),
            },
        )

        # Handle row selection
        selected_rows = []
        if isinstance(selection, dict):
            selected_rows = selection.get("selection", {}).get("rows", [])
        else:
            sel_obj = getattr(selection, "selection", None)
            if sel_obj:
                selected_rows = getattr(sel_obj, "rows", [])

        if selected_rows and len(selected_rows) > 0:
            idx = selected_rows[0]
            if idx < len(filtered_df):
                selected_pid = int(filtered_df.iloc[idx]["PID"])
                st.session_state.selected_pid = selected_pid

        # Action bar under table: CSV download & Quick selection indicator
        b_col1, b_col2 = st.columns([1.5, 1])
        with b_col1:
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="⬇️ Export Filtered Table to CSV",
                data=csv_data,
                file_name=f"pulseos_processes_{timestamp_str}.csv",
                mime="text/csv",
            )
        with b_col2:
            if st.session_state.selected_pid:
                st.caption(f"🎯 Target Process Selected: **PID {st.session_state.selected_pid}** (View in 'Deep-Dive Inspector' tab)")

        # Quick Inspector drawer if PID is selected
        if st.session_state.selected_pid:
            proc_diag = inspect_single_process(st.session_state.selected_pid)
            if "error" not in proc_diag:
                st.markdown(f"""
                <div class="inspector-box">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:1.15rem;font-weight:700;">🔍 Selected: {proc_diag['name']}</span>
                            <span class="code-chip" style="margin-left:8px;">PID {proc_diag['pid']}</span>
                            <span class="code-chip">PPID {proc_diag['ppid']} ({proc_diag['parent_name']})</span>
                        </div>
                        <div>
                            <span class="badge badge-cpu">{proc_diag['cpu_percent']:.1f}% CPU</span>
                            <span class="badge badge-io">{proc_diag['rss_mb']} MB RAM</span>
                        </div>
                    </div>
                    <div style="margin-top:10px;font-size:0.82rem;opacity:0.8;">
                        <b>Command:</b> <span class="code-chip">{proc_diag['cmdline'][:130]}...</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: SYSTEM TELEMETRY & PERFORMANCE
    # ------------------------------------------
    with tab_charts:
        chart_col1, chart_col2 = st.columns([1.3, 1])

        with chart_col1:
            st.subheader("System Load History (Real-Time Trend)")
            hist_df = pd.DataFrame(st.session_state.history)
            if not hist_df.empty and len(hist_df) > 1:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=hist_df["time"],
                    y=hist_df["CPU %"],
                    name="CPU %",
                    mode="lines",
                    line=dict(color="#3b82f6", width=2.5, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(59, 130, 246, 0.12)",
                ))
                fig_trend.add_trace(go.Scatter(
                    x=hist_df["time"],
                    y=hist_df["RAM %"],
                    name="RAM %",
                    mode="lines",
                    line=dict(color="#10b981", width=2.5, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(16, 185, 129, 0.08)",
                ))
                fig_trend.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[0, 100]),
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Accumulating metric samples in history buffer…")

        with chart_col2:
            st.subheader("Process Workload Breakdown")
            if total_procs > 0:
                counts = df["Estimate"].value_counts().reset_index()
                counts.columns = ["Estimate", "Count"]

                color_map = {
                    "CPU-bound": "#ef4444",
                    "I/O-bound": "#06b6d4",
                    "Balanced": "#10b981",
                    "Idle / Low CPU": "#64748b",
                    "Active (I/O unavail)": "#3b82f6",
                    "Mixed/Unknown": "#94a3b8",
                }
                pie_colors = [color_map.get(c, "#94a3b8") for c in counts["Estimate"]]

                fig_pie = go.Figure(data=[go.Pie(
                    labels=counts["Estimate"],
                    values=counts["Count"],
                    hole=0.6,
                    marker=dict(colors=pie_colors),
                    textinfo="label+percent",
                    insidetextorientation="radial",
                )])
                fig_pie.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    annotations=[dict(text=f"<b>{total_procs}</b><br>Tasks", x=0.5, y=0.5, font_size=15, showarrow=False)],
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No active process data available.")

        st.divider()

        # Multi-Core CPU Heatmap and System I/O Throughput
        core_col, io_col = st.columns([1.2, 1])
        with core_col:
            st.subheader("Per-Core CPU Utilization")
            core_names = [f"Core {i}" for i in range(len(per_cpu))]
            core_colors = ["#10b981" if v < 50 else "#f59e0b" if v < 80 else "#ef4444" for v in per_cpu]
            
            fig_cores = go.Figure(go.Bar(
                x=per_cpu,
                y=core_names,
                orientation="h",
                marker=dict(color=core_colors, line=dict(color="rgba(0,0,0,0.1)", width=1)),
                text=[f"{v:.1f}%" for v in per_cpu],
                textposition="auto",
            ))
            fig_cores.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_cores, use_container_width=True)

        with io_col:
            st.subheader("System-Wide I/O & Network Throughput")
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px;">
                <div class="kpi-card kpi-blue">
                    <div class="kpi-label">Disk Read Throughput</div>
                    <div class="kpi-value">{io_rates['disk_read_kbs']:.1f} <span style="font-size:0.9rem;">KB/s</span></div>
                    <div class="kpi-sub">Kernel block storage read</div>
                </div>
                <div class="kpi-card kpi-emerald">
                    <div class="kpi-label">Disk Write Throughput</div>
                    <div class="kpi-value">{io_rates['disk_write_kbs']:.1f} <span style="font-size:0.9rem;">KB/s</span></div>
                    <div class="kpi-sub">Kernel block storage write</div>
                </div>
                <div class="kpi-card kpi-amber">
                    <div class="kpi-label">Network Inbound</div>
                    <div class="kpi-value">{io_rates['net_down_kbs']:.1f} <span style="font-size:0.9rem;">KB/s</span></div>
                    <div class="kpi-sub">Ingress packet traffic</div>
                </div>
                <div class="kpi-card kpi-purple">
                    <div class="kpi-label">Network Outbound</div>
                    <div class="kpi-value">{io_rates['net_up_kbs']:.1f} <span style="font-size:0.9rem;">KB/s</span></div>
                    <div class="kpi-sub">Egress packet traffic</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Calculated differential rates across successive sampling cycles.")

    # ------------------------------------------
    # TAB 3: DEEP-DIVE PROCESS INSPECTOR & SIGNALS
    # ------------------------------------------
    with tab_inspector:
        st.subheader("Process Forensic Inspector & Signal Control")

        all_pids = sorted(df["PID"].tolist())
        default_index = 0
        if st.session_state.selected_pid in all_pids:
            default_index = all_pids.index(st.session_state.selected_pid)

        inspect_col1, inspect_col2 = st.columns([2, 1])
        with inspect_col1:
            chosen_pid = st.selectbox(
                "Select Target Process to Diagnose",
                options=all_pids,
                index=default_index,
                format_func=lambda pid: f"PID {pid} — {df.loc[df['PID'] == pid, 'Process'].values[0] if pid in df['PID'].values else 'Process'}",
            )
            st.session_state.selected_pid = chosen_pid

        with inspect_col2:
            st.write("")
            st.write("")
            if st.button("🔄 Reload Process Diagnostics", use_container_width=True):
                st.rerun()

        if chosen_pid:
            diag = inspect_single_process(chosen_pid)
            if "error" in diag:
                st.error(diag["error"])
            else:
                # Inspector Layout Cards
                i_row1, i_row2 = st.columns([1.5, 1])
                with i_row1:
                    st.markdown(f"""
                    <div class="inspector-box">
                        <div class="inspector-header">
                            <div>
                                <h3 style="margin:0;font-size:1.35rem;">{diag['name']}</h3>
                                <p style="margin:4px 0 0 0;font-size:0.84rem;opacity:0.75;">Owner: <b>{diag['username']}</b> · Status: <b>{diag['status']}</b></p>
                            </div>
                            <div>
                                <span class="badge badge-cpu">PID {diag['pid']}</span>
                                <span class="badge badge-io">PPID {diag['ppid']}</span>
                            </div>
                        </div>
                        <div style="font-size:0.86rem;line-height:1.7;">
                            <div><b>Executable Binary:</b> <span class="code-chip">{diag['exe']}</span></div>
                            <div style="margin-top:6px;"><b>Working Directory (CWD):</b> <span class="code-chip">{diag['cwd']}</span></div>
                            <div style="margin-top:6px;"><b>Command Line Arguments:</b><br><span class="code-chip">{diag['cmdline']}</span></div>
                            <div style="margin-top:8px;"><b>Process Parent:</b> <code>{diag['parent_name']}</code> (PID {diag['ppid']})</div>
                            <div><b>Started At:</b> {diag['create_time']} (Active duration: <b>{diag['uptime']}</b>)</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with i_row2:
                    st.markdown(f"""
                    <div class="inspector-box">
                        <h4 style="margin:0 0 12px 0;">Resource Footprint</h4>
                        <div style="font-size:0.88rem;line-height:2.0;">
                            <div>⚡ <b>CPU Load:</b> <code>{diag['cpu_percent']:.1f}%</code></div>
                            <div>⏱️ <b>User CPU Time:</b> <code>{diag['cpu_user']}</code></div>
                            <div>⚙️ <b>Kernel System Time:</b> <code>{diag['cpu_system']}</code></div>
                            <div>💾 <b>Resident Set Size (RSS):</b> <code>{diag['rss_mb']} MB</code></div>
                            <div>📦 <b>Virtual Memory Size (VMS):</b> <code>{diag['vms_mb']} MB</code></div>
                            <div>📊 <b>Memory Percentage:</b> <code>{diag['mem_percent']}%</code></div>
                            <div>🧵 <b>Active Threads:</b> <code>{diag['threads']}</code></div>
                            <div>📁 <b>Open File Descriptors:</b> <code>{diag['num_fds']}</code></div>
                            <div>⚖️ <b>Scheduler Nice Value:</b> <code>{diag['nice']}</code></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Process Signal Control Panel
                st.markdown("#### 🛡️ Operating System Signal Management")
                st.caption("Issue POSIX signals to the selected process with built-in safety protection against system anchors.")

                sig_col1, sig_col2, sig_col3 = st.columns([1, 1, 2])
                with sig_col1:
                    if st.button("⚠️ Terminate Gracefully (SIGTERM)", use_container_width=True):
                        signal_confirmation_modal(chosen_pid, diag['name'], "TERM")
                with sig_col2:
                    if st.button("🛑 Force Kill (SIGKILL)", type="primary", use_container_width=True):
                        signal_confirmation_modal(chosen_pid, diag['name'], "KILL")
                with sig_col3:
                    st.caption("Signals are guarded by kernel safeguards. Attempts to terminate PID 0, PID 1, or the host Streamlit engine are blocked.")

    # ------------------------------------------
    # TAB 4: OS ARCHITECTURE & HEURISTICS GUIDE
    # ------------------------------------------
    with tab_docs:
        st.subheader("Operating Systems Architecture & Profiling Methodology")

        st.markdown("""
        ### 1. Process Telemetry & Kernel State Machine
        Modern multitasking operating systems (Darwin/XNU, Linux, Windows NT) maintain process control blocks (PCBs) 
        managed by kernel schedulers (e.g. Linux CFS, Darwin Mach multi-queue priority scheduler).

        - **Process States:**
          - **Running / Runnable (`R`):** Actively scheduled on a logical processor core or waiting in the active runqueue.
          - **Interruptible Sleep (`S`):** Blocked waiting for an asynchronous event (timer, socket I/O, IPC mutex).
          - **Uninterruptible Disk Sleep (`D`):** In kernel space waiting directly for synchronous hardware response (e.g. disk page fault).
          - **Zombie (`Z`):** Terminated execution whose exit status has not yet been collected by its parent process via `waitpid()`.

        ---

        ### 2. Physical Memory vs Virtual Memory Architecture
        - **RSS (Resident Set Size):** Physical RAM pages mapped into the process's page tables at this exact sampling moment.
        - **VMS (Virtual Memory Size):** Total address space allocated by the process, including mapped shared libraries, memory-mapped files (`mmap`), and paged-out virtual pages.
        - **Page Replacement & Swapping:** When physical memory pressure occurs, the kernel paging daemon moves inactive anonymous pages to swap backing stores to preserve active working sets.

        ---

        ### 3. Transparent Workload Classification Heuristic
        The project implements an explainable, dual-parameter classification model:
        """)

        st.latex(r"""
        \text{Workload}(P) = \begin{cases}
        \text{CPU-bound}, & \text{if } \text{CPU}(P) \ge 20\% \\
        \text{I/O-bound}, & \text{if } \text{CPU}(P) < 10\% \text{ and } (\text{ReadRate} + \text{WriteRate}) \ge 64\text{ KiB/s} \\
        \text{Balanced / Idle}, & \text{otherwise}
        \end{cases}
        """)

        st.markdown("""
        > [!NOTE]
        > **OS Permissions & macOS Architecture:**
        > On macOS (Darwin), unprivileged user-space processes cannot read arbitrary task I/O counters due to 
        > Mach security boundaries and System Integrity Protection (SIP). When process-level I/O counters are restricted, 
        > the system transparently classifies high CPU tasks and provides real-time system-wide storage throughput 
        > via `psutil.disk_io_counters()`.
        """)


# Render cockpit
render_cockpit()
