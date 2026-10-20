# PulseOS — Process Cockpit & Kernel Telemetry Monitor
## Comprehensive Operating Systems Project Report

---

## 1. Executive Summary & Problem Statement
Operating systems manage compute, memory, and I/O hardware by scheduling concurrent processes across processor cores while arbitrating access to physical memory and storage. Standard command-line tools such as `top` and `ps` provide rudimentary snapshots but lack intuitive real-time trend analytics, interactive workload classification, and forensic inspection.

The primary objective of this project is to architect an interactive, browser-based operating system process manager (**PulseOS**) that:
1. Enumerates all active kernel and user processes, identifying process ancestry (PPID), user ownership, and lifecycle status.
2. Monitors CPU, physical memory (Resident Set Size), virtual memory (VMS), and differential per-process and system-wide I/O rates.
3. Classifies process workloads dynamically into **CPU-bound**, **I/O-bound**, or **Balanced** profiles using transparent heuristics.
4. Provides real-time telemetry visualizations (time-series utilization, per-core CPU heatmaps, workload distribution).
5. Enables deep-dive forensic inspection and controlled POSIX signal dispatching with safety guards against system disruption.

---

## 2. Tools & Architectural Framework
- **Core Engine:** Python 3.10+
- **Kernel Telemetry & OS Interfacing:** `psutil` (interfacing with Darwin Mach kernel APIs on macOS and `/proc` filesystem on Linux)
- **Data Modeling & Filtering:** `pandas`
- **Frontend Dashboard:** `Streamlit` (utilizing custom CSS styling, responsive layout grids, and non-blocking `@st.fragment` updates)
- **Data Visualizations:** `Plotly` (smooth spline area charts, multi-core utilization heatmaps, donut distributions)
- **Terminal CLI Interface:** `rich` (for live terminal table rendering)

---

## 3. System Design & Data Flow
```
+-------------------------------------------------------------+
|                  Operating System Kernel                    |
|    (Mach APIs / procfs / Host Statistics / Block I/O)       |
+------------------------------+------------------------------+
                               |
                               v
                     [ psutil Telemetry ]
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
   [ Process Metadata ]              [ System Telemetry ]
   - PID, PPID, User, Name           - Overall CPU & Load Avg
   - RSS / VMS Memory                - Per-Core CPU Load
   - Differential I/O Rates          - Disk & Net Throughput
              |                                 |
              +----------------+----------------+
                               |
                               v
          [ Heuristic Classification Engine ]
          - CPU-bound: CPU >= 20%
          - I/O-bound: CPU < 10% & I/O >= 64 KiB/s
          - Balanced / Idle: Normal activity
                               |
                               v
             [ Streamlit Cockpit UI Layer ]
   +-------------------------------------------------------+
   |  Tab 1: Process Explorer (Filters, Search, Table)     |
   |  Tab 2: Performance Telemetry (Charts & Heatmap)      |
   |  Tab 3: Deep-Dive Forensic Inspector & Signals        |
   |  Tab 4: OS Architecture & Documentation Guide         |
   +-------------------------------------------------------+
```

---

## 4. Workload Classification Heuristic & Mathematics

### Mathematical Formulation
$$W(P) = \begin{cases}
\text{CPU-bound}, & \text{if } \text{CPU}(P) \ge \theta_{\text{cpu}} \\
\text{I/O-bound}, & \text{if } \text{CPU}(P) < \theta_{\text{io\_cpu}} \text{ and } (\dot{R}_P + \dot{W}_P) \ge \theta_{\text{io}} \\
\text{Balanced / Idle}, & \text{otherwise}
\end{cases}$$

Where default calibrated parameters are:
- $\theta_{\text{cpu}} = 20.0\%$
- $\theta_{\text{io\_cpu}} = 10.0\%$
- $\theta_{\text{io}} = 64.0\text{ KiB/s}$

### Differential Rate Sampling
Because kernel hardware counters are monotonically increasing, throughput rates must be calculated differentially across discrete sampling epochs ($t_0$ to $t_1$):
$$\dot{R}_P = \frac{\text{ReadBytes}_{t_1} - \text{ReadBytes}_{t_0}}{t_1 - t_0}, \quad \dot{W}_P = \frac{\text{WriteBytes}_{t_1} - \text{WriteBytes}_{t_0}}{t_1 - t_0}$$

---

## 5. Implementation Highlights & UI Polish

1. **Human-Centric Visual Cockpit:**
   - Designed with clean, dark/light adaptive aesthetics, subtle glassmorphism headers, and live glowing status beacons.
   - 5-column executive KPI grid showing Active Processes, Overall CPU Load, Physical RAM in Use, Swap Allocation, and Workload Distribution.
2. **Interactive Process Explorer:**
   - Quick Filter Pills (`All Processes`, `User Apps`, `System Services`, `High CPU`, `High RAM`, `CPU-bound`, `I/O-bound`).
   - Top 5 CPU and Memory consumers quick-glance leaderboards.
   - Single-row table selection that instantly targets a process for inspection.
3. **Forensic Process Inspector:**
   - Deep inspection of PID, PPID, executable path, working directory (CWD), full command-line arguments, user vs kernel CPU times, RSS and VMS memory footprint, thread count, open file descriptors, and scheduler Nice priority.
4. **POSIX Signal Dispatcher & Safety Safeguards:**
   - Allows sending `SIGTERM` and `SIGKILL`.
   - Protects against terminating PID 0 (kernel), PID 1 (init/launchd), or the host dashboard engine.
   - Built-in `@st.dialog` modal requiring explicit confirmation.

---

## 6. Verification & Test Observations
- **Test 1 (Telemetry Stream & Pause):** Verified continuous background updates at configurable intervals (1s to 30s) as well as paused freeze mode for stationary inspection.
- **Test 2 (Dynamic Filtering & Sorting):** Tested instant preset filter pills and substring search across PID, name, and owner fields.
- **Test 3 (Heavy Workload Identification):** Spawned compute-intensive Python threads and verified that the heuristic engine tagged them as `CPU-bound` with elevated red progress bars.
- **Test 4 (Memory Monitoring):** Confirmed accurate reporting of physical RAM and swap allocation matching OS system monitors.
- **Test 5 (Export Functionality):** Verified CSV export of filtered tables with custom timestamped filenames.

---

## 7. Security Boundaries & Limitations
- **macOS SIP & Mach Boundaries:** macOS System Integrity Protection restricts reading unprivileged task I/O counters. The application handles this gracefully by surfacing available CPU metrics and supplementing system-wide storage throughput.
- **Process Kind Approximation:** UNIX-like operating systems do not provide a monolithic "user vs system" boolean. Classification is inferred through parent PID ancestry (`ppid == 1`) and system service account privileges.

---

## 8. Conclusion
PulseOS demonstrates a comprehensive, production-grade approach to operating system process monitoring. By bridging kernel telemetry with an intuitive, human-crafted web interface, it provides deep visibility into system performance, scheduling behavior, and resource utilization.
