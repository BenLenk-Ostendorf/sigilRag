"""
Pseudonym-based authentication module for the Siegel RAG system.
No real authentication - just user identification for logging purposes.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Optional


class PseudonymAuth:
    """Simple pseudonym-based authentication for user identification."""
    
    def __init__(self):
        self.session_key = "user_session"
        self.pseudonym_key = "user_pseudonym"
        self.user_id_key = "user_id"
        self.login_time_key = "login_time"
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has a pseudonym)."""
        return (
            self.pseudonym_key in st.session_state and 
            st.session_state[self.pseudonym_key] is not None and
            st.session_state[self.pseudonym_key].strip() != ""
        )
    
    def get_user_id(self) -> Optional[str]:
        """Get the current user's unique ID."""
        if self.is_authenticated():
            return st.session_state.get(self.user_id_key)
        return None
    
    def get_pseudonym(self) -> Optional[str]:
        """Get the current user's pseudonym."""
        if self.is_authenticated():
            return st.session_state.get(self.pseudonym_key)
        return None
    
    def get_login_time(self) -> Optional[datetime]:
        """Get the user's login time."""
        if self.is_authenticated():
            return st.session_state.get(self.login_time_key)
        return None
    
    def login(self, pseudonym: str) -> bool:
        """Login with a pseudonym."""
        if not pseudonym or pseudonym.strip() == "":
            return False
        
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        login_time = datetime.now()
        
        # Store in session state
        st.session_state[self.pseudonym_key] = pseudonym.strip()
        st.session_state[self.user_id_key] = user_id
        st.session_state[self.login_time_key] = login_time
        
        return True
    
    def logout(self):
        """Logout the current user."""
        keys_to_clear = [
            self.pseudonym_key,
            self.user_id_key,
            self.login_time_key,
            "chat_history",
            "messages"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def render_login_form(self):
        """Render the login form."""
        st.title("🏛️ Siegel RAG System")
        st.markdown("### Willkommen zum Siegel-Erstellungssystem")
        st.markdown("Bitte geben Sie ein Pseudonym ein, um zu beginnen:")
        
        with st.form("login_form"):
            pseudonym = st.text_input(
                "Pseudonym",
                placeholder="Ihr Pseudonym eingeben...",
                help="Wählen Sie einen beliebigen Namen zur Identifikation"
            )
            
            submitted = st.form_submit_button("Anmelden", use_container_width=True)
            
            if submitted:
                if self.login(pseudonym):
                    st.success(f"Willkommen, {pseudonym}!")
                    st.rerun()
                else:
                    st.error("Bitte geben Sie ein gültiges Pseudonym ein.")
    
    def render_user_info(self):
        """Render current user information."""
        if self.is_authenticated():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Angemeldet als:** {self.get_pseudonym()}")
            
            with col2:
                if st.button("Abmelden", key="logout_btn"):
                    self.logout()
                    st.rerun()
    
    def get_session_duration(self) -> Optional[float]:
        """Get current session duration in seconds."""
        login_time = self.get_login_time()
        if login_time:
            return (datetime.now() - login_time).total_seconds()
        return None
