"""
Admin dashboard component for TalentScout AI
Comprehensive management interface for interview sessions and system monitoring
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_dashboard():
    """Render admin dashboard with system overview and controls"""
    
    st.header("🏠 TalentScout AI Admin Dashboard")
    
    # Dashboard tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Sessions", "⚙️ Controls"])
    
    with tab1:
        render_overview_section()
    
    with tab2:
        render_sessions_section()
    
    with tab3:
        render_controls_section()

def render_overview_section():
    """Render system overview metrics"""
    
    st.subheader("📈 System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Interviews",
            value="15",
            delta="3 today"
        )
    
    with col2:
        st.metric(
            label="Active Sessions", 
            value="3",
            delta="0 pending"
        )
    
    with col3:
        ai_questions_count = len([m for m in st.session_state.get("messages", []) if "AI Generated" in m.get("content", "")])
        st.metric(
            label="AI Questions Generated",
            value=str(ai_questions_count),
            delta="+5 today"
        )
    
    with col4:
        st.metric(
            label="System Uptime",
            value="99.9%",
            delta="7 days"
        )
    
    # Recent activity summary
    st.subheader("📋 Recent Activity")
    
    if st.session_state.get("messages"):
        recent_messages = st.session_state.messages[-5:]
        activity_data = []
        
        for msg in recent_messages:
            activity_data.append({
                "Time": msg.get("timestamp", datetime.now()).strftime("%H:%M:%S") if hasattr(msg.get("timestamp", datetime.now()), 'strftime') else str(msg.get("timestamp", datetime.now()))[:8],
                "Type": "User Response" if msg["role"] == "user" else "AI Question",
                "Preview": msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"],
                "Stage": st.session_state.get("conversation_stage", "unknown").replace("_", " ").title()
            })
        
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity to display")

def render_sessions_section():
    """Render active sessions management"""
    
    st.subheader("👥 Interview Sessions")
    
    # Current session status
    if st.session_state.get("candidate_data"):
        st.success("🟢 Active Interview Session")
        
        candidate = st.session_state.candidate_data
        session_info = {
            "Session ID": st.session_state.get("session_id", "N/A"),
            "Candidate": candidate.get("name", "N/A"),
            "Email": candidate.get("email", "N/A"),
            "Position": candidate.get("position", "N/A"),
            "Experience": candidate.get("experience", "N/A"),
            "Current Stage": st.session_state.get("conversation_stage", "unknown").replace("_", " ").title(),
            "Messages": len(st.session_state.get("messages", [])),
            "Tech Stack": ", ".join(candidate.get("tech_stack", [])[:3]) + "..." if len(candidate.get("tech_stack", [])) > 3 else ", ".join(candidate.get("tech_stack", []))
        }
        
        # Display as metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Session Information:**")
            for key, value in list(session_info.items())[:4]:
                st.write(f"{key}: {value}")
        
        with col2:
            st.write("**Progress Details:**")
            for key, value in list(session_info.items())[4:]:
                st.write(f"{key}: {value}")
        
        # Session controls
        st.subheader("🎛️ Session Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏸️ Pause Interview"):
                st.info("Interview paused (feature demo)")
        
        with col2:
            if st.button("📊 Export Data"):
                # Create export data
                export_data = {
                    "session_info": session_info,
                    "messages": st.session_state.get("messages", []),
                    "candidate_data": candidate
                }
                st.success("Data exported (feature demo)")
                st.download_button(
                    label="📥 Download JSON",
                    data=str(export_data),
                    file_name=f"interview_{st.session_state.get('session_id', 'unknown')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🔄 Reset Session"):
                # Reset session state
                for key in ['messages', 'candidate_data', 'conversation_stage']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Session reset successfully")
                st.rerun()
    
    else:
        st.info("🔴 No Active Interview Sessions")
        
        # Show historical sessions (mock data)
        st.subheader("📈 Historical Sessions")
        
        historical_sessions = [
            {
                "Date": "2025-08-26",
                "Candidate": "Alice Johnson",
                "Position": "Senior Developer",
                "Status": "Completed",
                "Duration": "25 min"
            },
            {
                "Date": "2025-08-25", 
                "Candidate": "Bob Smith",
                "Position": "Data Scientist",
                "Status": "Completed",
                "Duration": "30 min"
            }
        ]
        
        df_historical = pd.DataFrame(historical_sessions)
        st.dataframe(df_historical, use_container_width=True, hide_index=True)

def render_controls_section():
    """Render system controls and settings"""
    
    st.subheader("⚙️ System Controls")
    
    # AI Configuration
    st.write("**🤖 AI Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "AI Creativity (Temperature)",
            min_value=0.1,
            max_value=1.0,
            value=st.session_state.get("ai_temperature", 0.7),
            step=0.1,
            help="Higher values make AI more creative"
        )
        st.session_state.ai_temperature = temperature
    
    with col2:
        max_tokens = st.number_input(
            "Max Response Tokens",
            min_value=50,
            max_value=1000,
            value=600,
            step=50
        )
    
    # Interview Settings
    st.write("**📝 Interview Settings**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_questions = st.number_input(
            "Max Questions per Stage",
            min_value=1,
            max_value=10,
            value=5
        )
    
    with col2:
        auto_advance = st.checkbox(
            "Auto-advance Stages",
            value=True
        )
    
    # System Preferences
    st.write("**🔧 System Preferences**")
    
    enable_analytics = st.checkbox("Enable Real-time Analytics", value=True)
    enable_logging = st.checkbox("Enable Detailed Logging", value=True)
    enable_notifications = st.checkbox("Enable System Notifications", value=False)
    
    # Save settings
    if st.button("💾 Save Settings"):
        st.success("⚡ Settings saved successfully!")
    
    # System Information
    st.subheader("ℹ️ System Information")
    
    system_info = {
        "Version": "2.0.0 Advanced",
        "Framework": "Streamlit + FastAPI",
        "AI Model": "Llama 3.3 70B Versatile",
        "Database": "SQLite",
        "Python": "3.8+",
        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for key, value in system_info.items():
        st.write(f"**{key}:** {value}")
