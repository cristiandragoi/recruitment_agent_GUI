@echo off
title CV Vorlage Filler - AP Arbeitspartner
echo.
echo  ========================================
echo   CV Vorlage Filler - AP Arbeitspartner
echo  ========================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause & exit /b 1
)
echo Installing / updating dependencies...
pip install -r requirements.txt -q --disable-pip-version-check
echo Starting app...
start "" http://localhost:8501
streamlit run app.py --server.headless false --browser.gatherUsageStats false
pause
