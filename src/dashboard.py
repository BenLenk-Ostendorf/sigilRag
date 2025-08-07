"""
Analytics dashboard for the Siegel RAG system.
Displays usage statistics, user interactions, and system metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any
from .logger import SiegelLogger
from .utils import format_timestamp


class SiegelDashboard:
    """Dashboard for displaying analytics and system metrics."""
    
    def __init__(self, logger: SiegelLogger):
        self.logger = logger
    
    def render(self):
        """Render the complete dashboard."""
        st.title("📊 Siegel RAG Dashboard")
        
        # Get data
        stats = self.logger.get_stats()
        interactions_df = self.logger.get_interactions_df()
        sessions_df = self.logger.get_sessions_df()
        errors_df = self.logger.get_errors_df()
        
        # Overview metrics
        self._render_overview_metrics(stats)
        
        # Charts and visualizations
        if not interactions_df.empty:
            self._render_usage_charts(interactions_df)
            self._render_user_activity(interactions_df)
            self._render_interaction_details(interactions_df)
        
        # Session information
        if not sessions_df.empty:
            self._render_session_info(sessions_df)
        
        # Error tracking
        if not errors_df.empty:
            self._render_error_tracking(errors_df)
        else:
            st.success("🎉 No errors recorded!")
        
        # Export functionality
        self._render_export_section()
    
    def _render_overview_metrics(self, stats: Dict[str, Any]):
        """Render overview metrics cards."""
        st.subheader("📈 Übersicht")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Gesamt Interaktionen",
                value=stats["total_interactions"]
            )
        
        with col2:
            st.metric(
                label="Eindeutige Nutzer",
                value=stats["unique_users"]
            )
        
        with col3:
            st.metric(
                label="Gesamt Sessions",
                value=stats["total_sessions"]
            )
        
        with col4:
            st.metric(
                label="Fehler",
                value=stats["total_errors"]
            )
        
        # Additional metrics
        if stats["total_interactions"] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_duration = stats["avg_session_duration"]
                if avg_duration:
                    st.metric(
                        label="Ø Session-Dauer",
                        value=f"{avg_duration:.1f}s"
                    )
            
            with col2:
                st.metric(
                    label="Ø Frage-Länge",
                    value=f"{stats['avg_question_length']:.0f} Zeichen"
                )
            
            with col3:
                st.metric(
                    label="Ø Antwort-Länge",
                    value=f"{stats['avg_answer_length']:.0f} Zeichen"
                )
    
    def _render_usage_charts(self, interactions_df: pd.DataFrame):
        """Render usage charts."""
        st.subheader("📊 Nutzungsstatistiken")
        
        # Interactions over time
        if 'timestamp' in interactions_df.columns:
            # Daily interactions
            interactions_df['date'] = interactions_df['timestamp'].dt.date
            daily_counts = interactions_df.groupby('date').size().reset_index(name='interactions')
            
            fig_daily = px.line(
                daily_counts,
                x='date',
                y='interactions',
                title='Tägliche Interaktionen',
                labels={'date': 'Datum', 'interactions': 'Anzahl Interaktionen'}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Hourly distribution
            interactions_df['hour'] = interactions_df['timestamp'].dt.hour
            hourly_counts = interactions_df.groupby('hour').size().reset_index(name='interactions')
            
            fig_hourly = px.bar(
                hourly_counts,
                x='hour',
                y='interactions',
                title='Interaktionen nach Tageszeit',
                labels={'hour': 'Stunde', 'interactions': 'Anzahl Interaktionen'}
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
    
    def _render_user_activity(self, interactions_df: pd.DataFrame):
        """Render user activity analysis."""
        st.subheader("👥 Nutzer-Aktivität")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top users by interactions
            user_counts = interactions_df['pseudonym'].value_counts().head(10)
            
            fig_users = px.bar(
                x=user_counts.values,
                y=user_counts.index,
                orientation='h',
                title='Top 10 Aktive Nutzer',
                labels={'x': 'Anzahl Interaktionen', 'y': 'Pseudonym'}
            )
            fig_users.update_layout(height=400)
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Session duration distribution
            if 'session_duration_seconds' in interactions_df.columns:
                fig_duration = px.histogram(
                    interactions_df,
                    x='session_duration_seconds',
                    nbins=20,
                    title='Verteilung Session-Dauer',
                    labels={'session_duration_seconds': 'Session-Dauer (Sekunden)', 'count': 'Anzahl'}
                )
                st.plotly_chart(fig_duration, use_container_width=True)
    
    def _render_interaction_details(self, interactions_df: pd.DataFrame):
        """Render detailed interaction analysis."""
        st.subheader("💬 Interaktions-Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Question length distribution
            fig_q_len = px.histogram(
                interactions_df,
                x='question_length',
                nbins=20,
                title='Verteilung Frage-Länge',
                labels={'question_length': 'Frage-Länge (Zeichen)', 'count': 'Anzahl'}
            )
            st.plotly_chart(fig_q_len, use_container_width=True)
        
        with col2:
            # Answer length distribution
            fig_a_len = px.histogram(
                interactions_df,
                x='answer_length',
                nbins=20,
                title='Verteilung Antwort-Länge',
                labels={'answer_length': 'Antwort-Länge (Zeichen)', 'count': 'Anzahl'}
            )
            st.plotly_chart(fig_a_len, use_container_width=True)
        
        # Recent interactions table
        st.subheader("🕒 Letzte Interaktionen")
        
        if not interactions_df.empty:
            recent_interactions = interactions_df.nlargest(10, 'timestamp')[
                ['timestamp', 'pseudonym', 'question', 'session_duration_seconds']
            ].copy()
            
            recent_interactions['timestamp'] = recent_interactions['timestamp'].apply(format_timestamp)
            recent_interactions['question'] = recent_interactions['question'].apply(
                lambda x: x[:100] + "..." if len(x) > 100 else x
            )
            
            st.dataframe(
                recent_interactions,
                column_config={
                    "timestamp": "Zeitstempel",
                    "pseudonym": "Nutzer",
                    "question": "Frage",
                    "session_duration_seconds": "Session-Dauer (s)"
                },
                use_container_width=True
            )
    
    def _render_session_info(self, sessions_df: pd.DataFrame):
        """Render session information."""
        st.subheader("🔄 Session-Informationen")
        
        # Session starts vs ends
        session_events = sessions_df['event'].value_counts()
        
        if len(session_events) > 0:
            fig_sessions = px.pie(
                values=session_events.values,
                names=session_events.index,
                title='Session-Events'
            )
            st.plotly_chart(fig_sessions, use_container_width=True)
        
        # Recent sessions
        if not sessions_df.empty:
            st.subheader("🕒 Letzte Sessions")
            recent_sessions = sessions_df.nlargest(10, 'timestamp')[
                ['timestamp', 'pseudonym', 'event']
            ].copy()
            
            recent_sessions['timestamp'] = recent_sessions['timestamp'].apply(format_timestamp)
            
            st.dataframe(
                recent_sessions,
                column_config={
                    "timestamp": "Zeitstempel",
                    "pseudonym": "Nutzer",
                    "event": "Event"
                },
                use_container_width=True
            )
    
    def _render_error_tracking(self, errors_df: pd.DataFrame):
        """Render error tracking information."""
        st.subheader("⚠️ Fehler-Tracking")
        
        # Error types
        error_types = errors_df['error_type'].value_counts()
        
        fig_errors = px.bar(
            x=error_types.index,
            y=error_types.values,
            title='Fehler-Typen',
            labels={'x': 'Fehler-Typ', 'y': 'Anzahl'}
        )
        st.plotly_chart(fig_errors, use_container_width=True)
        
        # Recent errors
        st.subheader("🕒 Letzte Fehler")
        recent_errors = errors_df.nlargest(10, 'timestamp')[
            ['timestamp', 'error_type', 'error_message']
        ].copy()
        
        recent_errors['timestamp'] = recent_errors['timestamp'].apply(format_timestamp)
        recent_errors['error_message'] = recent_errors['error_message'].apply(
            lambda x: x[:100] + "..." if len(x) > 100 else x
        )
        
        st.dataframe(
            recent_errors,
            column_config={
                "timestamp": "Zeitstempel",
                "error_type": "Fehler-Typ",
                "error_message": "Fehlermeldung"
            },
            use_container_width=True
        )
    
    def _render_export_section(self):
        """Render export functionality."""
        st.subheader("📤 Daten Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export als CSV", use_container_width=True):
                try:
                    exported_files = self.logger.export_to_csv()
                    if exported_files:
                        st.success("✅ CSV Export erfolgreich!")
                        for file_type, file_path in exported_files.items():
                            st.info(f"{file_type}: {file_path}")
                    else:
                        st.warning("Keine Daten zum Exportieren vorhanden.")
                except Exception as e:
                    st.error(f"Fehler beim CSV Export: {e}")
        
        with col2:
            if st.button("📋 Export als JSON", use_container_width=True):
                try:
                    exported_files = self.logger.export_to_json()
                    if exported_files:
                        st.success("✅ JSON Export erfolgreich!")
                        for file_type, file_path in exported_files.items():
                            st.info(f"{file_type}: {file_path}")
                    else:
                        st.warning("Keine Daten zum Exportieren vorhanden.")
                except Exception as e:
                    st.error(f"Fehler beim JSON Export: {e}")
        
        # System information
        st.subheader("🔧 System-Informationen")
        
        system_info = {
            "Aktueller Zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Log-Verzeichnis": str(self.logger.log_dir),
            "Verfügbare Log-Dateien": len(list(self.logger.log_dir.glob("*.jsonl")))
        }
        
        for key, value in system_info.items():
            st.info(f"**{key}:** {value}")
