# Siegel RAG System - Setup Guide

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key

### 2. Installation

#### Windows
```bash
# Clone or navigate to the project directory
cd SigilRAG

# Copy environment template
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here

# Run the application
run.bat
```

#### Linux/Mac
```bash
# Clone or navigate to the project directory
cd SigilRAG

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here

# Make script executable and run
chmod +x run.sh
./run.sh
```

#### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run application
streamlit run app.py
```

### 3. Configuration

#### Environment Variables (.env file)
```
OPENAI_API_KEY=your_openai_api_key_here
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

#### Streamlit Secrets (optional)
Create `.streamlit/secrets.toml` from the example file for additional configuration.

## 🎯 Features Overview

### 🔐 Authentication
- **Pseudonym-based login**: Simple user identification without real authentication
- **Session management**: Automatic session tracking and duration logging

### 💬 Chat Interface
- **RAG-powered responses**: Uses OpenAI GPT-4 with document retrieval
- **Session persistence**: Chat history maintained during session
- **Source citations**: Shows relevant document sources for each answer

### 📊 Analytics Dashboard
- **Usage statistics**: Track interactions, users, and system metrics
- **Visual analytics**: Charts and graphs for data visualization
- **Export functionality**: Download logs as CSV or JSON

### 🔧 System Management
- **Environment validation**: Check API keys and configuration
- **Vector store management**: Rebuild document index when needed
- **System testing**: Built-in test functionality

### 📋 Questionnaire Integration
- **Iframe support**: Embed external questionnaire tools
- **Flexible configuration**: Adjustable iframe dimensions and URLs

## 📁 Project Structure

```
SigilRAG/
├── app.py                 # Main Streamlit application
├── src/                   # Source code modules
│   ├── __init__.py
│   ├── auth.py           # Pseudonym authentication
│   ├── rag_system.py     # RAG implementation
│   ├── logger.py         # Comprehensive logging
│   ├── dashboard.py      # Analytics dashboard
│   └── utils.py          # Utility functions
├── data/                 # Data sources
│   ├── sigil_creation_guide.md
│   ├── sigil components/
│   └── complete_sigils/
├── logs/                 # Generated log files
├── vector_store/         # FAISS vector store
├── exports/              # Exported data files
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── run.bat              # Windows startup script
├── run.sh               # Linux/Mac startup script
└── README.md            # Project documentation
```

## 🔒 Security Features

- **API keys server-side only**: No sensitive data exposed to frontend
- **Environment variables**: Secure configuration management
- **Gitignore protection**: Sensitive files automatically excluded
- **No real authentication**: Simple pseudonym system for identification only

## 📝 Logging System

### Automatic Logging
- **User interactions**: Every question and answer logged
- **Session tracking**: Login/logout events with duration
- **Error tracking**: System errors and exceptions
- **Metadata**: Additional context and statistics

### Log Formats
- **JSON Lines**: Structured logging for easy parsing
- **Export options**: CSV and JSON export functionality
- **Real-time analytics**: Live dashboard updates

### Log Files
- `logs/interactions.jsonl`: User questions and answers
- `logs/sessions.jsonl`: Session start/end events
- `logs/errors.jsonl`: System errors and exceptions

## 🚨 Troubleshooting

### Common Issues

#### "OpenAI API key not found"
- Ensure `.env` file exists and contains valid API key
- Check that the key starts with `sk-`
- Verify the key has sufficient credits

#### "Vector store creation failed"
- Check that data files exist in the `data/` directory
- Ensure sufficient disk space for vector store
- Try rebuilding the vector store from the System page

#### "Module not found" errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the correct directory
- Verify virtual environment is activated

#### Streamlit won't start
- Check if port 8501 is already in use
- Try a different port in `.env` file
- Ensure Python and Streamlit are properly installed

### Performance Tips

- **Vector store**: Rebuilding is only needed when data changes
- **Memory usage**: Large document collections may require more RAM
- **API costs**: Monitor OpenAI usage to control costs
- **Caching**: Streamlit caches initialized systems for better performance

## 🔄 Updates and Maintenance

### Adding New Documents
1. Add files to the `data/` directory
2. Go to System page in the application
3. Click "Vector Store neu erstellen"
4. New documents will be indexed automatically

### Monitoring Usage
- Use the Dashboard page for real-time analytics
- Export logs regularly for long-term analysis
- Monitor API usage through OpenAI dashboard

### Backup and Recovery
- Backup the `logs/` directory regularly
- Export data before major updates
- Keep a copy of your `.env` configuration

## 📞 Support

For issues or questions:
1. Check this setup guide
2. Review the troubleshooting section
3. Check the system status page in the application
4. Verify all configuration files are correct
