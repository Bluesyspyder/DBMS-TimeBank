@echo off
call venv\Scripts\activate
echo Virtual environment activated!
echo Starting Streamlit app...
venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py
pause
