# Siegel RAG System

A Streamlit-based RAG (Retrieval-Augmented Generation) tool for answering questions about the Siegel-Erstellungssystem (Seal Creation System).

## Features

- **RAG System**: Uses OpenAI GPT-4 and LangChain to answer questions about seal creation
- **Pseudonym Login**: Simple user identification without real authentication
- **Chat Interface**: Interactive chat with session persistence
- **Comprehensive Logging**: All user interactions logged in JSON format
- **Export Functionality**: Logs exportable as CSV/JSON
- **Dashboard**: Quick stats and analytics
- **Iframe Integration**: Embedded questionnaire tool
- **Secure**: API keys handled server-side only

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your OpenAI API key
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
SigilRAG/
├── app.py                 # Main Streamlit application
├── src/
│   ├── auth.py           # Pseudonym authentication
│   ├── rag_system.py     # RAG implementation
│   ├── logger.py         # Logging functionality
│   ├── dashboard.py      # Analytics dashboard
│   └── utils.py          # Utility functions
├── data/                 # Data sources
│   ├── sigil_creation_guide.md
│   ├── sigil components/
│   └── complete_sigils/
├── logs/                 # Log files (created automatically)
├── vector_store/         # FAISS vector store (created automatically)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Usage

1. Start the application
2. Enter a pseudonym to begin
3. Ask questions about seal creation
4. View logs and statistics in the dashboard
5. Use the embedded questionnaire tool

## Data Sources

The system uses the following data sources:
- Seal creation guide (markdown)
- Seal components (images and descriptions)
- Complete seal examples (PNG files)

## Security

- API keys are stored server-side only
- No sensitive data exposed to frontend
- Environment variables properly configured
- Gitignore includes all sensitive files
