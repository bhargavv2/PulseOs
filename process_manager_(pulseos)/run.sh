#!/bin/bash
# Convenient one-click launcher for PulseOS Process Manager
cd "$(dirname "$0")"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    python -m streamlit run app.py
else
    echo "Virtual environment not found in .venv. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python -m streamlit run app.py
fi
