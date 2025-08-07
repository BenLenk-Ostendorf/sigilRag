@echo off
echo Starting Siegel RAG System...
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your OpenAI API key.
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run Streamlit app
echo.
echo Starting Streamlit application...
echo Open your browser to: http://localhost:8501
echo.
streamlit run app.py

pause
