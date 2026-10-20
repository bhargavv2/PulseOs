@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting PulseOS Process Cockpit
echo ========================================================

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python -m streamlit run app.py
) else (
    echo [1/3] Virtual environment not found. Creating .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [2/3] Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    echo [3/3] Launching Streamlit dashboard...
    python -m streamlit run app.py
)
pause
