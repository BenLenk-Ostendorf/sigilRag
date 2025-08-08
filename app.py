"""
Main Streamlit application for the Siegel RAG system.
Provides a chat interface for answering questions about seal creation.
"""

import streamlit as st
import os
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

# Import custom modules
from src.auth import CodeAuth
from src.rag_system import SiegelRAGSystem
from src.logger import SiegelLogger
from src.dashboard import SiegelDashboard
from src.utils import display_validation_status


# Page configuration
st.set_page_config(
    page_title="Siegel RAG System",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .source-doc {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        font-size: 0.8rem;
    }
    
    .iframe-container {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
# Force reset if using old auth class or incompatible session state
if ("auth" in st.session_state and 
    (st.session_state.auth.__class__.__name__ == "PseudonymAuth" or
     not hasattr(st.session_state.auth, 'is_admin'))):
    # Clear old session state to force reinitialization
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.messages = []
    st.session_state.rag_system = None
    st.session_state.logger = None
    st.session_state.auth = CodeAuth()

# Initialize components
@st.cache_resource
def initialize_systems():
    """Initialize RAG system and logger."""
    logger = SiegelLogger()
    rag_system = SiegelRAGSystem()
    
    if rag_system.initialize():
        return rag_system, logger
    else:
        return None, logger

def main():
    """Main application logic."""
    
    # Initialize systems if not done
    if not st.session_state.initialized:
        with st.spinner("🔄 Initialisiere System..."):
            rag_system, logger = initialize_systems()
            st.session_state.rag_system = rag_system
            st.session_state.logger = logger
            st.session_state.initialized = True
    
    auth = st.session_state.auth
    rag_system = st.session_state.rag_system
    logger = st.session_state.logger
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🏛️ Navigation")
        
        # Authentication status
        if auth.is_authenticated():
            auth.render_user_info()
            st.divider()
        
        # Navigation - Admin only for non-chat pages
        if auth.is_admin():
            page = st.selectbox(
                "Seite auswählen:",
                ["💬 Chat", "📊 Dashboard", "🔧 System"],
                index=0
            )
        else:
            # Regular users only see chat
            page = "💬 Chat"
            st.info("💬 Chat-Modus")
        
        # System status
        if rag_system:
            st.success("✅ RAG System bereit")
            vector_info = rag_system.get_vector_store_info()
            if vector_info["exists"]:
                st.info(f"📚 {vector_info.get('num_chunks', 0)} Dokument-Chunks")
        else:
            st.error("❌ RAG System nicht verfügbar")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Schnellaktionen")
        
        if st.button("🔄 Chat zurücksetzen"):
            st.session_state.messages = []
            if rag_system:
                rag_system.clear_memory()
            st.rerun()
        
        # Vector store rebuild - Admin only
        if auth.is_admin():
            if st.button("🔧 Vector Store neu erstellen") and rag_system:
                with st.spinner("Erstelle Vector Store neu..."):
                    rag_system.rebuild_vector_store()
                st.success("Vector Store neu erstellt!")
                st.rerun()
    
    # Main content based on selected page
    if not hasattr(auth, 'is_authenticated') or not auth.is_authenticated():
        auth.render_login_form()
    else:
        # Log session start if new session
        if "session_logged" not in st.session_state:
            try:
                # Try new method signature with group and admin info
                logger.log_session_start(
                    auth.get_user_id(), 
                    auth.get_code(), 
                    auth.get_group(),
                    auth.is_admin()
                )
            except TypeError:
                # Fallback to old method signature if needed
                logger.log_session_start(
                    auth.get_user_id(), 
                    auth.get_code() or "unknown"
                )
            st.session_state.session_logged = True
        
        if page == "💬 Chat":
            render_chat_page(rag_system, logger, auth)
        elif page == "📊 Dashboard":
            render_dashboard_page(logger)
        elif page == "🔧 System":
            render_system_page(rag_system)

def render_chat_page(rag_system, logger, auth):
    """Render the main chat interface."""
    st.title("💬 Siegel RAG Chat")
    st.markdown("Stellen Sie Fragen zum Siegel-Erstellungssystem!")
    
    if not rag_system:
        st.error("RAG System nicht verfügbar. Bitte überprüfen Sie Ihre Konfiguration.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📚 Quellen anzeigen"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Quelle {i+1}:**")
                        st.markdown(f"- **Typ:** {source.metadata.get('type', 'Unbekannt')}")
                        st.markdown(f"- **Quelle:** {source.metadata.get('source', 'Unbekannt')}")
                        st.markdown(f"- **Inhalt:** {source.page_content[:200]}...")
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ihre Frage zum Siegel-Erstellungssystem..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from RAG system
        with st.chat_message("assistant"):
            with st.spinner("🤔 Denke nach..."):
                answer, sources = rag_system.ask_question(prompt)
            
            st.markdown(answer)
            
            # Show sources
            if sources:
                with st.expander("📚 Quellen anzeigen"):
                    for i, source in enumerate(sources):
                        st.markdown(f"**Quelle {i+1}:**")
                        st.markdown(f"- **Typ:** {source.metadata.get('type', 'Unbekannt')}")
                        st.markdown(f"- **Quelle:** {source.metadata.get('source', 'Unbekannt')}")
                        st.markdown(f"- **Inhalt:** {source.page_content[:200]}...")
                        st.divider()
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer,
            "sources": sources
        })
        
        # Log interaction
        # Calculate session duration manually
        login_time = auth.get_login_time()
        session_duration = 0
        if login_time:
            from datetime import datetime
            session_duration = (datetime.now() - login_time).total_seconds()
        logger.log_interaction(
            user_id=auth.get_user_id(),
            pseudonym=auth.get_code(),
            question=prompt,
            answer=answer,
            session_duration=session_duration,
            metadata={
                "num_sources": len(sources),
                "source_types": [s.metadata.get('type') for s in sources]
            }
        )

def render_dashboard_page(logger):
    """Render the analytics dashboard."""
    dashboard = SiegelDashboard(logger)
    dashboard.render()

def render_system_page(rag_system):
    """Render system information and configuration."""
    st.title("🔧 System-Konfiguration")
    
    # Environment validation
    display_validation_status()
    
    st.divider()
    
    # RAG System information
    st.subheader("🤖 RAG System Status")
    
    if rag_system:
        vector_info = rag_system.get_vector_store_info()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vector Store", "✅ Verfügbar" if vector_info["exists"] else "❌ Nicht verfügbar")
        
        with col2:
            st.metric("Dokumente", vector_info.get("num_documents", 0))
        
        with col3:
            st.metric("Chunks", vector_info.get("num_chunks", 0))
        
        # Test query
        st.subheader("🧪 System Test")
        test_query = st.text_input("Test-Abfrage:", "Wie erstelle ich ein Siegel?")
        
        if st.button("Test ausführen"):
            with st.spinner("Teste System..."):
                answer, sources = rag_system.ask_question(test_query)
            
            st.success("✅ Test erfolgreich!")
            st.markdown(f"**Antwort:** {answer[:200]}...")
            st.markdown(f"**Quellen gefunden:** {len(sources)}")
    
    else:
        st.error("RAG System nicht verfügbar")
    
    st.divider()
    
    # Data files information
    st.subheader("📁 Daten-Dateien")
    
    from src.utils import get_data_files
    data_files = get_data_files("data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Markdown-Dateien", len(data_files["markdown"]))
        if data_files["markdown"]:
            with st.expander("Markdown-Dateien anzeigen"):
                for file in data_files["markdown"]:
                    st.text(file)
    
    with col2:
        st.metric("Bild-Dateien", len(data_files["images"]))
        if data_files["images"]:
            with st.expander("Bild-Dateien anzeigen"):
                for file in data_files["images"][:10]:  # Show first 10
                    st.text(file)
                if len(data_files["images"]) > 10:
                    st.text(f"... und {len(data_files['images']) - 10} weitere")
    
    with col3:
        st.metric("Verzeichnisse", len(data_files["directories"]))
        if data_files["directories"]:
            with st.expander("Verzeichnisse anzeigen"):
                for directory in data_files["directories"]:
                    st.text(directory)

if __name__ == "__main__":
    main()
