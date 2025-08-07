#!/bin/bash

echo "Starting Siegel RAG System..."
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key."
    echo
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run Streamlit app
echo
echo "Starting Streamlit application..."
echo "Open your browser to: http://localhost:8501"
echo
streamlit run app.py
