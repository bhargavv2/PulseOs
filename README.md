# Process Manager Dashboard (PulseOS)

A live system monitor and process manager built with Python, Streamlit, and `psutil`.

It tracks running processes in real time, graphs system-wide CPU and memory utilization, inspects individual process details (PPID, command-line arguments, threads, open files), and estimates whether an active task is **CPU-bound** or **I/O-bound** using resource heuristics.

Developed as an Operating Systems lab project. Includes both a web dashboard (`app.py`) and a terminal CLI tool (`process_manager.py`).

---

## Quick Start

Make sure you have **Python 3.10+** installed on your machine.

### On macOS / Linux
Open your terminal in the project folder and run:
```bash
./run.sh
```
*(If needed, run `chmod +x run.sh` once. The script checks for `.venv`, creates it if missing, installs dependencies, and starts Streamlit automatically).*

**Or manual setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### On Windows
Double-click **`run.bat`** in File Explorer.

**Or via Command Prompt / PowerShell:**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Once running, open your browser to **`http://localhost:8501`**.  
To stop the dashboard anytime, press `Ctrl + C` in the terminal.

---

## What It Does

### 1. Process Explorer & Filtering
- Displays all active processes: PID, process name, owner, status, CPU%, RAM (MB & %), thread count, and workload estimate.
- **Filter pills:** quickly filter by User Apps, System Services, High CPU (>10%), High RAM (>250MB), CPU-bound, or I/O-bound.
- **Search bar:** filter by process name, PID, or username as you type.
- **Top consumers:** side-by-side view showing the top 5 CPU and top 5 RAM consuming processes with visual bars.
- **Click to inspect:** clicking any row in the table opens that process in the inspector.
- **Export:** download the currently filtered table as a CSV file.

### 2. Live Resource Charts
- **Utilization History:** smoothed line chart tracking overall CPU % and RAM % over the last 60 sample updates.
- **Per-Core CPU:** horizontal bar breakdown showing each logical core individually (Core 0 to Core N).
- **Workload Pie/Donut:** distribution of CPU-bound vs I/O-bound vs balanced tasks.
- **System I/O:** differential disk read/write throughput and network download/upload rates.

### 3. Process Inspector & Signals
- Select any running process to view:
  - Parent PID (PPID) and parent process name
  - Full executable binary path and working directory
  - Full command-line launch arguments
  - Start time and running uptime
  - User vs Kernel CPU times, RSS vs Virtual memory (VMS), and Nice scheduler priority
- **Signal control:** send `SIGTERM` (graceful termination) or `SIGKILL` (force kill).
  - Built-in guards prevent terminating PID 0, PID 1, or the running dashboard itself.
  - Requires confirmation in a popup dialog before sending.

### 4. Terminal CLI Version
If you prefer a lightweight terminal tool without opening a browser:
```bash
python process_manager.py
```

---

## How Workload Classification Works

Operating systems do not explicitly tag processes as "CPU-bound" or "I/O-bound" in their process control blocks. That behavior has to be inferred from observed resource consumption.

This project uses an explainable heuristic:

- **CPU-bound:** Process is consuming $\ge 20\%$ CPU in the current sample window.
- **I/O-bound:** Process CPU is below $10\%$, but measured disk throughput (read + write) is $\ge 64\text{ KB/s}$.
- **Balanced / Idle:** Normal activity within balanced boundaries.

> **Note on macOS permissions:**  
> macOS restricts reading per-process I/O counters for unprivileged user-space processes (due to Mach kernel security and System Integrity Protection). When running on macOS without root, per-process I/O displays as `N/A`, but system-wide disk throughput is still tracked via `psutil.disk_io_counters()`. On Linux, per-process I/O is read directly from `/proc/[pid]/io`.

---

## Project Structure

```
├── app.py                  # Main Streamlit web dashboard
├── process_manager.py      # Terminal CLI version (built with rich)
├── requirements.txt        # Dependencies (psutil, streamlit, plotly, rich, pandas)
├── run.sh                  # 1-click launcher for macOS & Linux
├── run.bat                 # 1-click launcher for Windows
├── README.md               # Project documentation
├── PROJECT_REPORT_DRAFT.md # Technical report draft & viva notes
└── .vscode/
    ├── launch.json         # VS Code debug launcher (press F5 to run)
    └── settings.json       # Auto-selects .venv interpreter
```

---

## Common Issues & Troubleshooting

- **`zsh: command not found: python` (macOS):**  
  macOS uses `python3` by default. Activate the virtual environment first (`source .venv/bin/activate`), which provides the `python` alias, or just run `./run.sh`.
- **`Port 8501 is already in use`:**  
  Streamlit usually picks port 8502 automatically. If needed, specify a port manually:
  ```bash
  streamlit run app.py --server.port=8505
  ```
- **Windows PowerShell script execution error:**  
  Run this once in PowerShell to allow running local scripts:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
- **Sharing with another laptop:**  
  Do not copy the `.venv` folder to another laptop (virtual environments contain machine-specific absolute paths). Just copy the project files without `.venv`, then run `./run.sh` (Mac/Linux) or `run.bat` (Windows) so it builds its own virtual environment automatically.
