@echo off
REM Navigate to your project folder
cd /d "D:\health matrices"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install all required packages
pip install -r requirements.txt

REM Run your Streamlit dashboard app
streamlit run app1.py

pause
