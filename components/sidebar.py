"""
Enhanced sidebar with real-time AI insights for TalentScout AI
Updated for full integration with main app session state keys
"""

import streamlit as st
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Optional imports with graceful fallback
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def initialize_session_state():
    """Initialize session state with consistent keys"""
    defaults = {
        "current_stage": "greeting",
        "conversation_history": [],
        "interview_start_time": None,
        "candidate_info": {},
        "question_count": 0,
        "interview_started": False,
        "assessment_scores": [],
        "sentiment_history": [],
        "ai_response_times": []
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def render_sidebar():
    """Main sidebar rendering function"""
    try:
        initialize_session_state()
        
        with st.sidebar:
            render_header()
            st.markdown("---")
            render_progress()
            render_candidate_info()
            render_live_analytics()
            render_ai_insights()
            render_sentiment_chart()
            render_quality_metrics()
            render_controls()
            render_footer()
            
    except Exception as e:
        st.error(f"❌ Sidebar error: {e}")
        logger.error(f"Sidebar rendering error: {e}")


def render_header():
    """Render animated header with live stats"""
    try:
        ai_count = len([m for m in st.session_state.conversation_history 
                       if m.get("role") == "assistant" and "AI Generated" in m.get("content", "")])
        current_time = datetime.now().strftime("%H:%M:%S")
        
        st.markdown(f"""
        <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h1 style='margin: 0; font-size: 2rem;'>🎯</h1>
            <h3 style='margin: 0;'>TalentScout AI</h3>
            <p style='margin: 0; font-size: 0.9rem;'>AI Questions Generated: {ai_count}</p>
            <p style='margin: 0; font-size: 0.8rem;'>🕐 Live at {current_time}</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown("# 🎯 TalentScout AI")
        logger.error(f"Header error: {e}")


def render_progress():
    """Render interview progress with stage indicators"""
    try:
        stage = st.session_state.current_stage
        progress_mapping = {
            "greeting": 10,
            "info_collection": 30, 
            "technical_assessment": 60,
            "behavioral_assessment": 85,
            "wrap_up": 100
        }
        
        percentage = progress_mapping.get(stage, 5)
        st.subheader("📊 Interview Progress")
        st.progress(percentage / 100)
        st.caption(f"**Current Stage:** {stage.replace('_', ' ').title()}")
        
        # Stage indicators
        stages = [
            ("👋", "Greeting", "greeting"),
            ("📝", "Info Collection", "info_collection"),
            ("💻", "Technical", "technical_assessment"),
            ("🧠", "Behavioral", "behavioral_assessment"),
            ("✅", "Complete", "wrap_up")
        ]
        
        for icon, name, stage_key in stages:
            if stage_key == stage:
                st.success(f"{icon} **{name}** (Current)")
            elif progress_mapping.get(stage_key, 0) < percentage:
                st.success(f"{icon} ✅ {name}")
            else:
                st.write(f"{icon} ⏳ {name}")
                
    except Exception as e:
        st.error(f"Progress error: {e}")
        logger.error(f"Progress error: {e}")


def render_candidate_info():
    """Render candidate information panel"""
    try:
        candidate_info = st.session_state.candidate_info
        
        if not candidate_info:
            st.info("👤 Candidate information will appear here as the interview progresses.")
            return
            
        st.subheader("👤 Candidate Profile")
        
        # Calculate profile completeness
        required_fields = ["name", "email", "experience", "position", "tech_stack"]
        completed = sum(1 for field in required_fields if candidate_info.get(field))
        completeness = (completed / len(required_fields)) * 100
        
        # Completeness indicator
        if completeness >= 80:
            st.success(f"📊 Profile: {completeness:.0f}% Complete")
        elif completeness >= 50:
            st.info(f"📊 Profile: {completeness:.0f}% Complete")
        else:
            st.warning(f"📊 Profile: {completeness:.0f}% Complete")
        
        # Display candidate info
        field_icons = {
            "name": "👤",
            "email": "📧",
            "experience": "⏰",
            "position": "🎯",
            "tech_stack": "💻"
        }
        
        for key, value in candidate_info.items():
            if value:
                icon = field_icons.get(key, "📌")
                st.write(f"{icon} **{key.replace('_', ' ').title()}:** {value}")
                
    except Exception as e:
        st.error(f"Candidate info error: {e}")
        logger.error(f"Candidate info error: {e}")


def render_live_analytics():
    """Render real-time analytics"""
    try:
        messages = st.session_state.conversation_history
        
        if len(messages) < 3:
            st.info("📈 Analytics will populate as the interview progresses.")
            return
            
        st.subheader("📈 Live Analytics")
        
        # Calculate metrics
        user_messages = [m for m in messages if m.get("role") == "user"]
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        ai_generated = [m for m in ai_messages if "AI Generated" in m.get("content", "")]
        
        # Metrics in columns
        col1, col2 = st.columns(2)
        
        with col1:
            if user_messages:
                avg_length = sum(len(m.get("content", "")) for m in user_messages) / len(user_messages)
                st.metric("📝 Avg Response", f"{avg_length:.0f} chars")
            else:
                st.metric("📝 Avg Response", "0 chars")
                
        with col2:
            st.metric("🤖 AI Questions", len(ai_generated))
        
        # Engagement indicator
        if user_messages:
            avg_words = sum(len(m.get("content", "").split()) for m in user_messages) / len(user_messages)
            if avg_words > 50:
                st.success("🔥 High engagement")
            elif avg_words > 20:
                st.info("👍 Good engagement") 
            else:
                st.warning("💬 Brief responses")
                
    except Exception as e:
        st.error(f"Analytics error: {e}")
        logger.error(f"Analytics error: {e}")


def render_ai_insights():
    """Render AI generation insights"""
    try:
        messages = st.session_state.conversation_history
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        ai_generated = [m for m in ai_messages if "AI Generated" in m.get("content", "")]
        
        if len(ai_messages) > 2:
            st.subheader("🤖 AI Insights")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🧠 Total AI", len(ai_generated))
            with col2:
                if ai_messages:
                    efficiency = (len(ai_generated) / len(ai_messages)) * 100
                    st.metric("⚡ Efficiency", f"{efficiency:.0f}%")
                    
    except Exception as e:
        st.error(f"AI insights error: {e}")
        logger.error(f"AI insights error: {e}")


def render_sentiment_chart():
    """Render sentiment analysis chart"""
    try:
        if not PLOTLY_AVAILABLE:
            return
            
        sentiment_history = st.session_state.sentiment_history
        
        if len(sentiment_history) > 2:
            st.subheader("😊 Sentiment Trend")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=sentiment_history,
                mode='lines+markers',
                name='Sentiment',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                yaxis_title="Sentiment"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        logger.error(f"Sentiment chart error: {e}")


def render_quality_metrics():
    """Render response quality metrics"""
    try:
        messages = st.session_state.conversation_history
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        
        if len(ai_messages) > 2:
            st.subheader("⭐ Quality Metrics")
            
            avg_length = sum(len(m.get("content", "")) for m in ai_messages) / len(ai_messages)
            avg_words = sum(len(m.get("content", "").split()) for m in ai_messages) / len(ai_messages)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📏 Avg Length", f"{avg_length:.0f}")
            with col2:
                st.metric("📝 Avg Words", f"{avg_words:.0f}")
                
            # Quality indicator
            if avg_words > 100:
                st.success("🔥 Comprehensive responses")
            elif avg_words > 50:
                st.info("👍 Detailed responses")
            else:
                st.warning("💬 Concise responses")
                
    except Exception as e:
        st.error(f"Quality metrics error: {e}")
        logger.error(f"Quality metrics error: {e}")


def render_controls():
    """Render control buttons"""
    try:
        st.markdown("---")
        st.subheader("🎛️ Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset", use_container_width=True, type="secondary"):
                reset_session()
                st.rerun()
                
        with col2:
            if st.button("📥 Export", use_container_width=True, type="primary"):
                export_data()
                
    except Exception as e:
        st.error(f"Controls error: {e}")
        logger.error(f"Controls error: {e}")


def render_footer():
    """Render sidebar footer with stats"""
    try:
        st.markdown("---")
        
        # Session stats
        message_count = len(st.session_state.conversation_history)
        user_responses = len([m for m in st.session_state.conversation_history if m.get("role") == "user"])
        question_count = st.session_state.question_count
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Messages", message_count)
        with col2:
            st.metric("❓ Questions", question_count)
            
        # Duration
        if st.session_state.interview_start_time:
            duration = (datetime.now() - st.session_state.interview_start_time).seconds // 60
            st.metric("⏱️ Duration", f"{duration} min")
            
        # Footer info
        st.caption("🚀 TalentScout AI Advanced v2.0")
        st.caption("🤖 Powered by Llama 3.3 70B")
        st.caption(f"🕐 Updated: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Footer error: {e}")


def reset_session():
    """Reset interview session"""
    try:
        keys_to_reset = [
            "conversation_history", "candidate_info", "question_count",
            "interview_started", "assessment_scores", "sentiment_history", "ai_response_times"
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                if key == "question_count":
                    st.session_state[key] = 0
                elif key == "interview_started":
                    st.session_state[key] = False
                else:
                    st.session_state[key] = [] if isinstance(st.session_state[key], list) else {}
                    
        st.session_state.current_stage = "greeting"
        st.session_state.interview_start_time = datetime.now()
        st.success("✅ Session reset successfully!")
        
    except Exception as e:
        st.error(f"Reset error: {e}")
        logger.error(f"Reset error: {e}")


def export_data():
    """Export interview data as JSON"""
    try:
        export_data = {
            "session_info": {
                "start_time": str(st.session_state.interview_start_time),
                "current_stage": st.session_state.current_stage,
                "duration_minutes": (datetime.now() - st.session_state.interview_start_time).seconds // 60 if st.session_state.interview_start_time else 0
            },
            "candidate_info": st.session_state.candidate_info,
            "conversation_history": st.session_state.conversation_history,
            "analytics": {
                "total_messages": len(st.session_state.conversation_history),
                "questions_asked": st.session_state.question_count,
                "assessment_scores": st.session_state.assessment_scores,
                "sentiment_history": st.session_state.sentiment_history
            }
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Interview Data",
            data=json_data,
            file_name=f"interview_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Export error: {e}")
        logger.error(f"Export error: {e}")
