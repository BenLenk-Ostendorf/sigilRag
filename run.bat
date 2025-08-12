@echo off
echo Starting Siegel RAG System...
echo.

REM Check if .env file exists (optional - we use Streamlit secrets)
if not exist .env (
    echo INFO: .env file not found - using Streamlit secrets instead.
    echo If running locally, make sure .streamlit/secrets.toml is configured.
    echo.
)

REM Check if virtual environment exists
if not exist .venv (
    if not exist venv (
        echo Creating virtual environment...
        python -m venv .venv
    ) else (
        echo Using existing venv directory...
    )
)

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    call venv\Scripts\activate.bat
)

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