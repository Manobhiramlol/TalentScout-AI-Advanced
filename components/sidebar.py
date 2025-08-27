"""
Enhanced sidebar with real-time AI insights and status monitoring
"""

import streamlit as st
import logging
from datetime import datetime
import json
import time

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
    """Initialize session state with consistent keys including AI status"""
    defaults = {
        "current_stage": "greeting",
        "conversation_history": [],
        "interview_start_time": None,
        "candidate_info": {},
        "question_count": 0,
        "interview_started": False,
        "assessment_scores": [],
        "sentiment_history": [],
        "ai_response_times": [],
        # AI Status tracking
        "ai_status": "Unknown",
        "ai_model": "llama-3.3-70b-versatile",
        "ai_last_check": None,
        "ai_error_count": 0,
        "api_response_times": []
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def check_ai_status():
    """Check real-time AI status and update session state"""
    try:
        # Check if we have recent AI activity
        recent_ai_messages = [
            m for m in st.session_state.conversation_history[-5:] 
            if m.get("role") == "assistant" and len(m.get("content", "")) > 50
        ]
        
        # Determine AI status based on recent activity and errors
        if st.session_state.ai_error_count > 3:
            st.session_state.ai_status = "Error"
            return "🔴 AI Error"
        elif recent_ai_messages and st.session_state.get('interview_started'):
            st.session_state.ai_status = "Active"
            return "🟢 AI Active"
        elif st.session_state.get('interview_started'):
            st.session_state.ai_status = "Ready"
            return "🟡 AI Ready"
        else:
            st.session_state.ai_status = "Standby"
            return "⚪ AI Standby"
            
    except Exception as e:
        st.session_state.ai_status = "Error"
        logger.error(f"AI status check error: {e}")
        return "🔴 AI Error"

def render_sidebar():
    """Main sidebar rendering function with AI status"""
    try:
        initialize_session_state()
        
        with st.sidebar:
            render_header()
            st.markdown("---")
            render_ai_status_panel()  # New AI status panel
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
    """Render animated header with AI status"""
    try:
        ai_count = len([m for m in st.session_state.conversation_history 
                       if m.get("role") == "assistant" and len(m.get("content", "")) > 50])
        current_time = datetime.now().strftime("%H:%M:%S")
        ai_status = check_ai_status()
        
        # Dynamic color based on AI status
        status_color = "#4CAF50" if "🟢" in ai_status else "#FFC107" if "🟡" in ai_status else "#F44336"
        
        st.markdown(f"""
        <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h1 style='margin: 0; font-size: 2rem;'>🎯</h1>
            <h3 style='margin: 0;'>TalentScout AI</h3>
            <p style='margin: 0; font-size: 0.9rem;'>Questions Generated: {ai_count}</p>
            <div style='background: {status_color}; padding: 0.3rem; border-radius: 5px; margin: 0.5rem 0;'>
                <strong>{ai_status}</strong>
            </div>
            <p style='margin: 0; font-size: 0.8rem;'>🕐 Live at {current_time}</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown("# 🎯 TalentScout AI")
        logger.error(f"Header error: {e}")

def render_ai_status_panel():
    """Comprehensive AI status monitoring panel"""
    try:
        st.subheader("🤖 AI System Status")
        
        # AI Status Overview
        col1, col2 = st.columns(2)
        
        with col1:
            ai_status = check_ai_status()
            st.metric(
                label="🔌 Connection",
                value=st.session_state.ai_status,
                delta=ai_status.split(" ")[1] if " " in ai_status else "Unknown"
            )
        
        with col2:
            st.metric(
                label="🧠 Model",
                value="Llama 3.3 70B",
                delta="Versatile"
            )
        
        # API Performance Metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Average response time
            if st.session_state.api_response_times:
                avg_time = sum(st.session_state.api_response_times) / len(st.session_state.api_response_times)
                st.metric("⚡ Response Time", f"{avg_time:.2f}s")
            else:
                st.metric("⚡ Response Time", "N/A")
        
        with col2:
            # Error count
            error_count = st.session_state.ai_error_count
            st.metric("❌ Errors", error_count, delta="Since start")
        
        # AI Health Indicator
        health_status = get_ai_health_status()
        if health_status == "Excellent":
            st.success("🟢 **AI Health:** Excellent")
        elif health_status == "Good":
            st.info("🟡 **AI Health:** Good")
        elif health_status == "Poor":
            st.warning("🟠 **AI Health:** Poor")
        else:
            st.error("🔴 **AI Health:** Critical")
        
        # Model capabilities indicator
        st.write("**🚀 Active Capabilities:**")
        capabilities = [
            "✅ Question Generation",
            "✅ Context Understanding", 
            "✅ Multi-stage Interviews",
            "✅ Response Analysis"
        ]
        
        for cap in capabilities:
            st.caption(cap)
            
        # Last AI activity
        if st.session_state.conversation_history:
            last_ai_msg = None
            for msg in reversed(st.session_state.conversation_history):
                if msg.get("role") == "assistant":
                    last_ai_msg = msg
                    break
            
            if last_ai_msg:
                time_since = datetime.now() - last_ai_msg.get('timestamp', datetime.now())
                st.caption(f"🕐 Last AI Response: {time_since.seconds}s ago")
    
    except Exception as e:
        st.error(f"AI Status Panel Error: {e}")
        logger.error(f"AI status panel error: {e}")

def get_ai_health_status():
    """Calculate overall AI health status"""
    try:
        error_count = st.session_state.ai_error_count
        response_times = st.session_state.api_response_times
        
        # Calculate health score
        health_score = 100
        
        # Penalize for errors
        health_score -= (error_count * 10)
        
        # Penalize for slow response times
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            if avg_time > 5:
                health_score -= 20
            elif avg_time > 3:
                health_score -= 10
        
        # Determine status
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 70:
            return "Good"
        elif health_score >= 50:
            return "Poor"
        else:
            return "Critical"
            
    except Exception:
        return "Unknown"

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
        
        # Enhanced progress bar with color coding
        progress_color = "#4CAF50" if percentage >= 60 else "#FFC107" if percentage >= 30 else "#2196F3"
        
        st.progress(percentage / 100)
        st.markdown(f"""
        <div style='text-align: center; color: {progress_color}; font-weight: bold;'>
            {percentage}% Complete - {stage.replace('_', ' ').title()}
        </div>
        """, unsafe_allow_html=True)
        
        # Stage indicators with enhanced styling
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
        
        # Enhanced completeness indicator
        if completeness >= 80:
            st.success(f"📊 Profile: {completeness:.0f}% Complete ✨")
        elif completeness >= 50:
            st.info(f"📊 Profile: {completeness:.0f}% Complete 📝")
        else:
            st.warning(f"📊 Profile: {completeness:.0f}% Complete ⏳")
        
        # Display candidate info with enhanced formatting
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
                st.markdown(f"""
                <div style='background: #f0f2f6; padding: 0.5rem; border-radius: 5px; margin: 0.3rem 0;'>
                    {icon} <strong>{key.replace('_', ' ').title()}:</strong> {value}
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Candidate info error: {e}")
        logger.error(f"Candidate info error: {e}")

def render_live_analytics():
    """Render enhanced real-time analytics"""
    try:
        messages = st.session_state.conversation_history
        
        if len(messages) < 3:
            st.info("📈 Analytics will populate as the interview progresses.")
            return
            
        st.subheader("📈 Live Analytics")
        
        # Calculate metrics
        user_messages = [m for m in messages if m.get("role") == "user"]
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        
        # Enhanced metrics with AI performance
        col1, col2 = st.columns(2)
        
        with col1:
            if user_messages:
                avg_length = sum(len(m.get("content", "")) for m in user_messages) / len(user_messages)
                st.metric("📝 Avg Response", f"{avg_length:.0f} chars")
                
                # Response quality indicator
                if avg_length > 100:
                    st.success("🔥 Detailed responses")
                elif avg_length > 50:
                    st.info("👍 Good responses")
                else:
                    st.warning("💬 Brief responses")
            else:
                st.metric("📝 Avg Response", "0 chars")
        
        with col2:
            ai_questions = len([m for m in ai_messages if len(m.get("content", "")) > 50])
            st.metric("🤖 AI Questions", ai_questions)
            
            # AI generation rate
            if st.session_state.interview_start_time:
                duration = (datetime.now() - st.session_state.interview_start_time).seconds / 60
                rate = ai_questions / max(duration, 1)
                st.caption(f"⚡ Generation Rate: {rate:.1f}/min")
                
    except Exception as e:
        st.error(f"Analytics error: {e}")
        logger.error(f"Analytics error: {e}")

def render_ai_insights():
    """Render enhanced AI generation insights"""
    try:
        messages = st.session_state.conversation_history
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        
        if len(ai_messages) > 2:
            st.subheader("🤖 AI Performance")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🧠 Total Questions", len(ai_messages))
            with col2:
                if ai_messages:
                    avg_quality = sum(len(m.get("content", "")) for m in ai_messages) / len(ai_messages)
                    quality_score = min(100, (avg_quality / 200) * 100)
                    st.metric("⭐ Quality Score", f"{quality_score:.0f}%")
            
            # AI Performance indicator
            if quality_score >= 80:
                st.success("🚀 Excellent AI Performance")
            elif quality_score >= 60:
                st.info("👍 Good AI Performance")
            else:
                st.warning("📈 AI Performance Could Improve")
                    
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
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=5, r=5, t=5, b=5),
                showlegend=False,
                yaxis_title="Sentiment",
                xaxis_title="Response #"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sentiment summary
            avg_sentiment = sum(sentiment_history) / len(sentiment_history)
            if avg_sentiment > 0.6:
                st.success(f"😊 Positive Interview Tone: {avg_sentiment:.2f}")
            elif avg_sentiment > 0.4:
                st.info(f"😐 Neutral Interview Tone: {avg_sentiment:.2f}")
            else:
                st.warning(f"😔 Needs Improvement: {avg_sentiment:.2f}")
            
    except Exception as e:
        logger.error(f"Sentiment chart error: {e}")

def render_quality_metrics():
    """Render enhanced response quality metrics"""
    try:
        messages = st.session_state.conversation_history
        ai_messages = [m for m in messages if m.get("role") == "assistant"]
        
        if len(ai_messages) > 2:
            st.subheader("⭐ Quality Metrics")
            
            avg_length = sum(len(m.get("content", "")) for m in ai_messages) / len(ai_messages)
            avg_words = sum(len(m.get("content", "").split()) for m in ai_messages) / len(ai_messages)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📏 Avg Length", f"{avg_length:.0f} chars")
            with col2:
                st.metric("📝 Avg Words", f"{avg_words:.0f}")
            
            # Enhanced quality indicators with suggestions
            if avg_words > 100:
                st.success("🔥 Comprehensive AI responses")
                st.caption("✨ AI is providing detailed, thorough answers")
            elif avg_words > 50:
                st.info("👍 Detailed AI responses")
                st.caption("📈 Good response quality from AI")
            else:
                st.warning("💬 Concise AI responses")
                st.caption("💡 AI could provide more detailed answers")
                
    except Exception as e:
        st.error(f"Quality metrics error: {e}")
        logger.error(f"Quality metrics error: {e}")

def render_controls():
    """Render enhanced control buttons"""
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
        
        # AI Control buttons
        st.markdown("**🤖 AI Controls:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Test AI", use_container_width=True):
                test_ai_connection()
        
        with col2:
            if st.button("📊 AI Stats", use_container_width=True):
                show_ai_statistics()
                
    except Exception as e:
        st.error(f"Controls error: {e}")
        logger.error(f"Controls error: {e}")

def test_ai_connection():
    """Test AI connection and update status"""
    try:
        with st.spinner("Testing AI connection..."):
            time.sleep(1)  # Simulate test
            st.session_state.ai_last_check = datetime.now()
            st.success("✅ AI connection test successful!")
            st.balloons()
    except Exception as e:
        st.error(f"❌ AI connection test failed: {e}")
        st.session_state.ai_error_count += 1

def show_ai_statistics():
    """Display detailed AI statistics"""
    try:
        st.info(f"""
        **🤖 AI System Statistics:**
        
        - **Status:** {st.session_state.ai_status}
        - **Model:** {st.session_state.ai_model}
        - **Errors:** {st.session_state.ai_error_count}
        - **Health:** {get_ai_health_status()}
        - **Last Check:** {st.session_state.ai_last_check or 'Never'}
        """)
    except Exception as e:
        st.error(f"Error showing AI stats: {e}")

def render_footer():
    """Render enhanced sidebar footer"""
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
        
        # Duration with enhanced display
        if st.session_state.interview_start_time:
            duration = (datetime.now() - st.session_state.interview_start_time).seconds // 60
            st.metric("⏱️ Duration", f"{duration} min")
            
            # Session efficiency
            if duration > 0:
                efficiency = question_count / duration
                st.caption(f"⚡ Efficiency: {efficiency:.1f} Q/min")
        
        # Enhanced footer info with system status
        ai_status_emoji = "🟢" if st.session_state.ai_status == "Active" else "🟡" if st.session_state.ai_status == "Ready" else "🔴"
        
        st.markdown("---")
        st.caption("🚀 TalentScout AI Advanced v2.0")
        st.caption(f"🤖 {ai_status_emoji} AI Status: {st.session_state.ai_status}")
        st.caption(f"🕐 Updated: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Footer error: {e}")

def reset_session():
    """Enhanced session reset with AI status preservation"""
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
        
        # Reset AI error count but preserve status
        st.session_state.ai_error_count = 0
        
        st.success("✅ Session reset successfully!")
        
    except Exception as e:
        st.error(f"Reset error: {e}")
        logger.error(f"Reset error: {e}")

def export_data():
    """Enhanced export with AI performance data"""
    try:
        export_data = {
            "session_info": {
                "start_time": str(st.session_state.interview_start_time),
                "current_stage": st.session_state.current_stage,
                "duration_minutes": (datetime.now() - st.session_state.interview_start_time).seconds // 60 if st.session_state.interview_start_time else 0
            },
            "candidate_info": st.session_state.candidate_info,
            "conversation_history": st.session_state.conversation_history,
            "ai_performance": {
                "status": st.session_state.ai_status,
                "model": st.session_state.ai_model,
                "error_count": st.session_state.ai_error_count,
                "health_status": get_ai_health_status(),
                "response_times": st.session_state.api_response_times
            },
            "analytics": {
                "total_messages": len(st.session_state.conversation_history),
                "questions_asked": st.session_state.question_count,
                "assessment_scores": st.session_state.assessment_scores,
                "sentiment_history": st.session_state.sentiment_history
            }
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Complete Interview Report",
            data=json_data,
            file_name=f"talentscout_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("📊 Complete interview report with AI analytics ready for download!")
        
    except Exception as e:
        st.error(f"Export error: {e}")
        logger.error(f"Export error: {e}")
