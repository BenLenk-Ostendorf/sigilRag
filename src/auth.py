"""
Pseudonym-based authentication module for the Siegel RAG system.
No real authentication - just user identification for logging purposes.
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Optional


class CodeAuth:
    """Code-based authentication with group assignment for research participants."""
    
    def __init__(self):
        self.session_key = "user_session"
        self.code_key = "user_code"
        self.user_id_key = "user_id"
        self.login_time_key = "login_time"
        self.group_key = "user_group"
        self.admin_key = "is_admin"
        
        # Admin password from Streamlit secrets
        try:
            self.admin_password = st.secrets["general"]["ADMIN_PASSWORD"]
        except KeyError:
            # Fallback for development/testing
            self.admin_password = "admin2024"
            st.warning("⚠️ Admin password not found in secrets. Using default password for development.")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (has a valid code)."""
        return (
            self.code_key in st.session_state and 
            st.session_state[self.code_key] is not None and
            st.session_state[self.code_key].strip() != ""
        )
    
    def get_user_id(self) -> Optional[str]:
        """Get the current user's unique ID."""
        if self.is_authenticated():
            return st.session_state.get(self.user_id_key)
        return None
    
    def get_code(self) -> Optional[str]:
        """Get the current user's access code."""
        if self.is_authenticated():
            return st.session_state.get(self.code_key)
        return None
    
    def get_group(self) -> Optional[int]:
        """Get the current user's group (1=Video, 2=RAG GPT, 3=explAIner)."""
        if self.is_authenticated():
            return st.session_state.get(self.group_key)
        return None
    
    def is_admin(self) -> bool:
        """Check if current user has admin privileges."""
        return st.session_state.get(self.admin_key, False)
    
    def get_login_time(self) -> Optional[datetime]:
        """Get the user's login time."""
        if self.is_authenticated():
            return st.session_state.get(self.login_time_key)
        return None
    
    def parse_code(self, code: str) -> Optional[dict]:
        """Parse the access code and extract group information.
        Format: G[Gruppe]C[CASE]W221T4FH
        Example: G2C0001W221T4FH -> Group 2, Case 1
        """
        if not code or len(code) < 12:
            return None
        
        code = code.strip().upper()
        
        # Check format: G[digit]C[4digits]W221T4FH
        if not code.startswith('G') or 'C' not in code or not code.endswith('W221T4FH'):
            return None
        
        try:
            # Extract group (position 1)
            group = int(code[1])
            if group not in [1, 2, 3]:  # Valid groups: 1=Video, 2=RAG GPT, 3=explAIner
                return None
            
            # Find 'C' position and extract case number
            c_pos = code.find('C')
            if c_pos == -1 or c_pos + 5 >= len(code):
                return None
            
            case_str = code[c_pos + 1:c_pos + 5]
            if not case_str.isdigit():
                return None
            
            case_num = int(case_str)
            
            return {
                'group': group,
                'case': case_num,
                'code': code
            }
        except (ValueError, IndexError):
            return None
    
    def login(self, code: str) -> bool:
        """Login with an access code."""
        parsed = self.parse_code(code)
        if not parsed:
            return False
        
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        login_time = datetime.now()
        
        # Store in session state
        st.session_state[self.code_key] = parsed['code']
        st.session_state[self.group_key] = parsed['group']
        st.session_state[self.user_id_key] = user_id
        st.session_state[self.login_time_key] = login_time
        st.session_state[self.admin_key] = False  # Regular user
        
        return True
    
    def admin_login(self, password: str) -> bool:
        """Admin login with password."""
        if password == self.admin_password:
            # Generate unique admin ID
            user_id = "admin_" + str(uuid.uuid4())
            login_time = datetime.now()
            
            # Store admin session
            st.session_state[self.code_key] = "ADMIN"
            st.session_state[self.group_key] = 0  # Admin group
            st.session_state[self.user_id_key] = user_id
            st.session_state[self.login_time_key] = login_time
            st.session_state[self.admin_key] = True
            
            return True
        return False
    
    def logout(self):
        """Logout the current user."""
        keys_to_clear = [
            self.code_key,
            self.group_key,
            self.user_id_key,
            self.login_time_key,
            self.admin_key,
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
        st.markdown("Bitte geben Sie Ihren Zugangscode ein:")
        
        # Main login form
        with st.form("login_form"):
            access_code = st.text_input(
                "Zugangscode",
                placeholder="G2C0001W221T4FH",
                help="Format: G[Gruppe]C[Fall]W221T4FH"
            )
            
            submitted = st.form_submit_button("Anmelden", use_container_width=True)
            
            if submitted:
                if self.login(access_code):
                    group_names = {1: "Video", 2: "RAG GPT", 3: "explAIner"}
                    group_name = group_names.get(self.get_group(), "Unbekannt")
                    st.success(f"Willkommen! Gruppe: {group_name}")
                    st.rerun()
                else:
                    st.error("Ungültiger Zugangscode. Bitte überprüfen Sie das Format.")
        
        # Admin login (collapsible)
        with st.expander("🔧 Admin-Zugang"):
            with st.form("admin_form"):
                admin_password = st.text_input(
                    "Admin-Passwort",
                    type="password",
                    help="Nur für Administratoren"
                )
                
                admin_submitted = st.form_submit_button("Admin-Anmeldung")
                
                if admin_submitted:
                    if self.admin_login(admin_password):
                        st.success("Admin-Zugang gewährt!")
                        st.rerun()
                    else:
                        st.error("Falsches Admin-Passwort.")
    
    def render_user_info(self):
        """Render current user information."""
        if self.is_authenticated():
            if self.is_admin():
                st.markdown("**🔧 Admin-Modus aktiv**")
            else:
                group_names = {1: "Video", 2: "RAG GPT", 3: "explAIner"}
                group_name = group_names.get(self.get_group(), "Unbekannt")
                st.markdown(f"**Gruppe:** {group_name}")
                st.markdown(f"**Code:** {self.get_code()}")
            
            # Note: No logout button as requested - session ends when browser closes
    
    def get_session_duration(self) -> Optional[float]:
        """Get current session duration in seconds."""
        login_time = self.get_login_time()
        if login_time:
            return (datetime.now() - login_time).total_seconds()
        return None
