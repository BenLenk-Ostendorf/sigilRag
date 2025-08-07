"""
Utility functions for the Siegel RAG system.
"""

import os
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
import base64


def load_css(file_path: str) -> str:
    """Load CSS from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_base64_of_bin_file(bin_file: str) -> str:
    """Convert binary file to base64 string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def load_image_as_base64(image_path: str) -> str:
    """Load image and convert to base64 for embedding in HTML."""
    return get_base64_of_bin_file(image_path)


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing problematic characters."""
    import re
    # Replace problematic characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    # Remove leading/trailing underscores
    safe_name = safe_name.strip('_')
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def get_data_files(data_dir: str) -> Dict[str, List[str]]:
    """Get all data files organized by type."""
    data_path = Path(data_dir)
    
    files = {
        "markdown": [],
        "images": [],
        "directories": []
    }
    
    if not data_path.exists():
        return files
    
    for item in data_path.rglob("*"):
        if item.is_file():
            if item.suffix.lower() in ['.md', '.txt']:
                files["markdown"].append(str(item))
            elif item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                files["images"].append(str(item))
        elif item.is_dir():
            files["directories"].append(str(item))
    
    return files


def create_download_link(data: bytes, filename: str, link_text: str) -> str:
    """Create a download link for binary data."""
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
    return href


def validate_environment() -> Dict[str, bool]:
    """Validate that all required environment variables are set."""
    required_vars = [
        "OPENAI_API_KEY"
    ]
    
    validation = {}
    for var in required_vars:
        validation[var] = bool(os.getenv(var))
    
    return validation


def display_validation_status():
    """Display environment validation status in Streamlit."""
    validation = validate_environment()
    
    st.subheader("🔧 Environment Status")
    
    for var, is_valid in validation.items():
        if is_valid:
            st.success(f"✅ {var} is configured")
        else:
            st.error(f"❌ {var} is missing")
            st.info(f"Please set {var} in your .env file")


def format_timestamp(timestamp) -> str:
    """Format timestamp for display."""
    if hasattr(timestamp, 'strftime'):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return str(timestamp)


def clean_text_for_embedding(text: str) -> str:
    """Clean text for better embedding quality."""
    import re
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with embedding
    text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"]', ' ', text)
    
    # Remove multiple consecutive punctuation
    text = re.sub(r'[.,!?;:]+', lambda m: m.group()[0], text)
    
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            sentence_ends = ['.', '!', '?', '\n\n']
            best_break = end
            
            for i in range(end - 100, end):
                if i > 0 and text[i-1] in sentence_ends and text[i] == ' ':
                    best_break = i
                    break
            
            end = best_break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks
