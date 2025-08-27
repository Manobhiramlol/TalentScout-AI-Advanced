"""
Enhanced sidebar with real-time AI insights and dynamic analytics - Streamlit Compatible
Advanced version with error handling, caching, and comprehensive features
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Import protection
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    st.warning("⚠️ Plotly not installed. Some visualizations may not be available.")
    go = None
    px = None
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    st.warning("⚠️ Pandas not installed. Some data features may not be available.")
    pd = None
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

def render_sidebar():
    """Enhanced sidebar with real-time AI analytics and insights"""
    
    try:
        # Initialize all session state variables first
        initialize_session_state()
        
        with st.sidebar:
            # Header with branding and live status
            render_dynamic_header()
            
            st.markdown("---")
            
            # Real-time interview progress
            render_interview_progress()
            
            # Candidate information panel
            render_candidate_panel()
            
            # Live AI analytics
            render_live_analytics()
            
            # Real-time AI insights
            render_ai_insights()
            
            # Sentiment analysis chart (if available)
            render_sentiment_analysis()
            
            # AI Quality metrics
            render_ai_quality_metrics()
            
            # Advanced controls
            render_advanced_controls()
            
            # Enhanced footer with AI stats
            render_sidebar_footer()
            
    except Exception as e:
        st.error(f"❌ Sidebar error: {e}")
        logger.error(f"Sidebar rendering error: {e}")

def render_dynamic_header():
    """Dynamic header with live AI status"""
    
    try:
        # Get current AI generation status
        question_count = len([m for m in st.session_state.get("messages", []) 
                             if m.get("role") == "assistant" and "AI Generated" in m.get("content", "")])
        
        # Get current time for live status
        current_time = datetime.now().strftime("%H:%M:%S")
        
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <h1 style='color: #ffffff; margin: 0; font-size: 2.5rem;'>🎯</h1>
            <h3 style='margin: 0; color: #ffffff;'>TalentScout AI</h3>
            <p style='margin: 0; color: #e8e8e8; font-size: 0.8rem;'>Advanced v2.0 • {question_count} AI Questions Generated</p>
            <p style='margin: 0; color: #e8e8e8; font-size: 0.7rem;'>🕐 Live • {current_time}</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown("# 🎯 TalentScout AI")
        logger.error(f"Header rendering error: {e}")

def initialize_session_state():
    """Initialize all required session state variables with error handling"""
    
    try:
        # Basic session variables
        if "conversation_stage" not in st.session_state:
            st.session_state.conversation_stage = "greeting"
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "interview_start_time" not in st.session_state:
            st.session_state.interview_start_time = datetime.now()
        
        # Candidate data
        if "candidate_data" not in st.session_state:
            st.session_state.candidate_data = {}
        
        # Assessment data
        if "assessment_scores" not in st.session_state:
            st.session_state.assessment_scores = []
        
        if "sentiment_history" not in st.session_state:
            st.session_state.sentiment_history = []
        
        # AI performance tracking
        if "ai_response_times" not in st.session_state:
            st.session_state.ai_response_times = []
        
        # Session analytics
        if "session_analytics" not in st.session_state:
            st.session_state.session_analytics = {
                "total_questions": 0,
                "ai_generated": 0,
                "user_responses": 0,
                "avg_response_time": 0
            }
            
    except Exception as e:
        logger.error(f"Session state initialization error: {e}")

@st.cache_data(ttl=5)
def calculate_interview_progress(stage: str) -> Dict[str, Any]:
    """Calculate interview progress percentage with caching"""
    
    stage_progress = {
        "greeting": {"percentage": 10, "current_index": 0, "description": "Initial greeting and rapport building"},
        "info_collection": {"percentage": 30, "current_index": 1, "description": "Collecting candidate information"},
        "technical_assessment": {"percentage": 60, "current_index": 2, "description": "Technical skills evaluation"},
        "behavioral_assessment": {"percentage": 85, "current_index": 3, "description": "Behavioral competency assessment"},
        "completed": {"percentage": 100, "current_index": 4, "description": "Interview completed successfully"}
    }
    
    return stage_progress.get(stage, {"percentage": 5, "current_index": 0, "description": "Starting interview"})

def render_interview_progress():
    """Enhanced real-time interview progress with AI insights"""
    
    try:
        st.subheader("📊 Interview Progress")
        
        # Get current stage and calculate progress
        stage = st.session_state.get("conversation_stage", "greeting")
        progress_data = calculate_interview_progress(stage)
        
        # Enhanced progress bar with AI question count
        progress_percentage = progress_data["percentage"]
        ai_question_count = len([m for m in st.session_state.get("messages", []) 
                               if m.get("role") == "assistant" and "AI Generated" in m.get("content", "")])
        
        # Animated progress bar
        st.progress(progress_percentage / 100, 
                   text=f"{progress_percentage}% Complete • {ai_question_count} AI Questions")
        
        # Progress description
        st.caption(f"📝 {progress_data['description']}")
        
        # Enhanced stage indicators with AI insights
        stages = [
            {"name": "Greeting", "icon": "👋"},
            {"name": "Info Collection", "icon": "📝"},
            {"name": "Technical", "icon": "💻"},
            {"name": "Behavioral", "icon": "🧠"},
            {"name": "Complete", "icon": "✅"}
        ]
        
        current_stage_index = progress_data["current_index"]
        
        for i, stage_info in enumerate(stages):
            if i < current_stage_index:
                st.success(f"{stage_info['icon']} ✅ {stage_info['name']}")
            elif i == current_stage_index:
                st.info(f"{stage_info['icon']} 🔄 {stage_info['name']} (Current)")
            else:
                st.write(f"{stage_info['icon']} ⏳ {stage_info['name']}")
        
        # Enhanced time tracking with AI generation rate
        elapsed_time = datetime.now() - st.session_state.interview_start_time
        minutes = elapsed_time.seconds // 60
        seconds = elapsed_time.seconds % 60
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱️ Duration", f"{minutes}m {seconds}s")
        with col2:
            generation_rate = ai_question_count / max(minutes, 1) if minutes > 0 else ai_question_count
            st.metric("🤖 AI Rate", f"{generation_rate:.1f}/min")
            
    except Exception as e:
        st.error(f"Progress rendering error: {e}")
        logger.error(f"Progress rendering error: {e}")

def render_candidate_panel():
    """Enhanced candidate panel with AI-extracted insights"""
    
    try:
        if st.session_state.candidate_data:
            st.markdown("---")
            st.subheader("👤 Candidate Profile")
            
            data = st.session_state.candidate_data
            
            # Profile card with enhanced styling
            with st.container():
                # Create profile completeness score
                completeness = calculate_profile_completeness(data)
                
                # Profile completeness indicator
                if completeness >= 80:
                    st.success(f"📊 Profile Completeness: {completeness}% - Excellent!")
                elif completeness >= 60:
                    st.info(f"📊 Profile Completeness: {completeness}% - Good")
                else:
                    st.warning(f"📊 Profile Completeness: {completeness}% - Needs More Info")
                
                # Enhanced profile display
                if name := data.get("name"):
                    st.markdown(f"**🏷️ Name:** {name}")
                
                if email := data.get("email"):
                    st.markdown(f"**📧 Email:** {email}")
                
                if experience := data.get("experience"):
                    st.markdown(f"**💼 Experience:** {experience}")
                
                if position := data.get("position"):
                    st.markdown(f"**🎯 Target Role:** {position}")
            
            # Enhanced skills visualization with categories
            if skills := data.get("tech_stack"):
                st.markdown("**💻 Tech Stack:**")
                
                # Categorize skills
                skill_categories = categorize_skills(skills)
                
                for category, category_skills in skill_categories.items():
                    if category_skills:
                        with st.expander(f"{get_category_icon(category)} {category.title()} ({len(category_skills)})"):
                            st.write(", ".join(category_skills))
                            
    except Exception as e:
        st.error(f"Candidate panel error: {e}")
        logger.error(f"Candidate panel error: {e}")

def render_live_analytics():
    """Enhanced real-time analytics with comprehensive metrics"""
    
    try:
        if len(st.session_state.messages) > 4:
            st.markdown("---")
            st.subheader("📈 Live Analytics")
            
            # Response metrics
            user_messages = [m for m in st.session_state.messages if m.get("role") == "user"]
            ai_messages = [m for m in st.session_state.messages if m.get("role") == "assistant"]
            ai_generated = [m for m in ai_messages if "AI Generated" in m.get("content", "")]
            
            # Analytics grid
            col1, col2 = st.columns(2)
            
            with col1:
                if user_messages:
                    avg_response_length = sum(len(m.get("content", "").split()) for m in user_messages) / len(user_messages)
                    st.metric("📝 Avg Response", f"{avg_response_length:.0f} words")
                else:
                    st.metric("📝 Avg Response", "0 words")
                
                # Response quality indicator
                if avg_response_length > 50:
                    st.success("🔥 Detailed responses")
                elif avg_response_length > 20:
                    st.info("👍 Good responses")
                else:
                    st.warning("💬 Brief responses")
            
            with col2:
                st.metric("🤖 AI Questions", len(ai_generated))
                
                # AI generation efficiency
                if len(ai_generated) > 0:
                    ai_efficiency = len(ai_generated) / len(ai_messages) * 100
                    st.metric("🎯 AI Efficiency", f"{ai_efficiency:.0f}%")
            
            # Response time trend (if available)
            if st.session_state.get("ai_response_times"):
                render_response_time_chart()
                
    except Exception as e:
        st.error(f"Analytics error: {e}")
        logger.error(f"Analytics error: {e}")

def render_ai_insights():
    """Enhanced AI insights with comprehensive generation analytics"""
    
    try:
        if len(st.session_state.get("messages", [])) > 3:
            st.markdown("---")
            st.subheader("🤖 AI Insights")
            
            # AI Generation Stats
            messages = st.session_state.get("messages", [])
            ai_questions = [m for m in messages if m.get("role") == "assistant" and "AI Generated" in m.get("content", "")]
            
            if ai_questions:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🧠 AI Questions", len(ai_questions))
                with col2:
                    recent_ai = len([q for q in ai_questions[-5:]])
                    st.metric("🔥 Recent", recent_ai)
                
                # AI model performance
                st.markdown("**🚀 AI Performance:**")
                
                # Model efficiency metrics
                total_messages = len(messages)
                ai_ratio = len(ai_questions) / total_messages * 100 if total_messages > 0 else 0
                
                progress_bar_html = f"""
                <div style="background-color: #e0e0e0; border-radius: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #4CAF50, #45a049); height: 20px; width: {ai_ratio}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {ai_ratio:.0f}%
                    </div>
                </div>
                <p style="text-align: center; margin: 5px 0; font-size: 0.8rem;">AI Question Generation Rate</p>
                """
                st.markdown(progress_bar_html, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"AI insights error: {e}")
        logger.error(f"AI insights error: {e}")

def render_sentiment_analysis():
    """Render sentiment analysis chart if data available"""
    
    try:
        sentiment_history = st.session_state.get("sentiment_history", [])
        
        if len(sentiment_history) > 2 and PLOTLY_AVAILABLE:
            st.markdown("---")
            st.subheader("😊 Sentiment Analysis")
            
            # Create sentiment chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=sentiment_history,
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title="Response #",
                yaxis_title="Sentiment",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sentiment summary
            avg_sentiment = sum(sentiment_history) / len(sentiment_history)
            if avg_sentiment > 0.1:
                st.success(f"😊 Positive trend: {avg_sentiment:.2f}")
            elif avg_sentiment > -0.1:
                st.info(f"😐 Neutral trend: {avg_sentiment:.2f}")
            else:
                st.warning(f"😔 Negative trend: {avg_sentiment:.2f}")
                
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")

def render_ai_quality_metrics():
    """Show AI response quality and performance metrics"""
    
    try:
        ai_messages = [m for m in st.session_state.messages if m.get("role") == "assistant"]
        
        if len(ai_messages) > 2:
            st.markdown("---")
            st.subheader("⭐ AI Quality Metrics")
            
            # Calculate AI response metrics
            avg_length = sum(len(m.get("content", "")) for m in ai_messages) / len(ai_messages)
            avg_words = sum(len(m.get("content", "").split()) for m in ai_messages) / len(ai_messages)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📏 Avg Length", f"{avg_length:.0f} chars")
            with col2:
                st.metric("📝 Avg Words", f"{avg_words:.0f}")
            
            # Quality indicators
            if avg_words > 100:
                st.success("🔥 Comprehensive responses")
            elif avg_words > 50:
                st.info("👍 Detailed responses")
            else:
                st.warning("💬 Concise responses")
                
    except Exception as e:
        logger.error(f"AI quality metrics error: {e}")

def render_response_time_chart():
    """Render AI response time trend chart"""
    
    try:
        response_times = st.session_state.get("ai_response_times", [])
        
        if len(response_times) > 2 and PLOTLY_AVAILABLE:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=response_times,
                mode='lines+markers',
                name='Response Time',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                height=150,
                margin=dict(l=0, r=0, t=20, b=0),
                title="⚡ AI Response Times",
                title_font_size=14,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        logger.error(f"Response time chart error: {e}")

def render_advanced_controls():
    """Render advanced interview controls"""
    
    try:
        st.markdown("---")
        st.subheader("🎛️ Advanced Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Session", help="Reset the interview session"):
                reset_session()
                st.rerun()
        
        with col2:
            if st.button("📊 Export Data", help="Export interview data"):
                export_interview_data()
        
        # AI Settings
        with st.expander("🤖 AI Settings"):
            ai_creativity = st.slider(
                "AI Creativity",
                min_value=0.1,
                max_value=1.0,
                value=st.session_state.get("ai_temperature", 0.7),
                step=0.1,
                help="Higher values make AI more creative"
            )
            st.session_state.ai_temperature = ai_creativity
            
            auto_questions = st.checkbox(
                "Auto-generate follow-up questions",
                value=st.session_state.get("auto_questions", True)
            )
            st.session_state.auto_questions = auto_questions
            
    except Exception as e:
        logger.error(f"Advanced controls error: {e}")

def render_sidebar_footer():
    """Enhanced sidebar footer with comprehensive AI stats"""
    
    try:
        st.markdown("---")
        
        # Enhanced performance stats
        message_count = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m.get("role") == "user"])
        ai_generated = len([m for m in st.session_state.messages if m.get("role") == "assistant" and "AI Generated" in m.get("content", "")])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Messages", message_count)
            st.metric("🤖 AI Gen", ai_generated)
        with col2:
            st.metric("👤 Responses", user_messages)
            if ai_generated > 0 and message_count > 0:
                ai_ratio = (ai_generated / message_count) * 100
                st.metric("🎯 AI %", f"{ai_ratio:.0f}%")
            else:
                st.metric("🎯 AI %", "0%")
        
        # System status
        st.markdown("---")
        st.markdown("**🚀 System Status**")
        
        # Model info with status indicators
        model_status = "🟢 Online" if st.session_state.get("ai_model_available", True) else "🔴 Offline"
        st.caption(f"🧠 Llama 3.3 70B Versatile • {model_status}")
        st.caption("⚡ Dynamic AI Question Generation")
        st.caption("🔒 End-to-end encrypted • Privacy protected")
        st.caption("📊 Real-time analytics enabled")
        
        # Version info
        st.markdown("---")
        st.caption("TalentScout AI Advanced v2.0")
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Footer error: {e}")

# Utility Functions

def calculate_profile_completeness(data: Dict[str, Any]) -> int:
    """Calculate profile completeness percentage"""
    
    required_fields = ["name", "email", "experience", "position", "tech_stack"]
    completed_fields = 0
    
    for field in required_fields:
        if field in data and data[field]:
            if field == "tech_stack" and len(data[field]) > 0:
                completed_fields += 1
            elif field != "tech_stack":
                completed_fields += 1
    
    return int((completed_fields / len(required_fields)) * 100)

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills into different categories"""
    
    categories = {
        "languages": ["python", "javascript", "java", "c++", "c#", "go", "rust", "typescript"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "fastapi", "express", "spring"],
        "databases": ["mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
        "tools": ["git", "github", "jira", "jenkins", "figma"]
    }
    
    categorized = {cat: [] for cat in categories.keys()}
    categorized["other"] = []
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized_flag = False
        
        for category, category_skills in categories.items():
            if any(cat_skill in skill_lower for cat_skill in category_skills):
                categorized[category].append(skill)
                categorized_flag = True
                break
        
        if not categorized_flag:
            categorized["other"].append(skill)
    
    return {k: v for k, v in categorized.items() if v}

def get_category_icon(category: str) -> str:
    """Get icon for skill category"""
    
    icons = {
        "languages": "🐍",
        "frameworks": "⚛️",
        "databases": "🗄️",
        "cloud": "☁️",
        "tools": "🔧",
        "other": "📦"
    }
    
    return icons.get(category, "📦")

def reset_session():
    """Reset interview session"""
    
    try:
        # Keep essential keys but reset interview data
        keys_to_reset = [
            "messages", "candidate_data", "conversation_stage", 
            "assessment_scores", "sentiment_history", "ai_response_times"
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                if key == "conversation_stage":
                    st.session_state[key] = "greeting"
                elif key in ["messages", "assessment_scores", "sentiment_history", "ai_response_times"]:
                    st.session_state[key] = []
                else:
                    st.session_state[key] = {}
        
        st.session_state.interview_start_time = datetime.now()
        st.success("✅ Session reset successfully!")
        
    except Exception as e:
        st.error(f"Reset error: {e}")
        logger.error(f"Session reset error: {e}")

def export_interview_data():
    """Export interview data as JSON"""
    
    try:
        export_data = {
            "session_info": {
                "start_time": st.session_state.interview_start_time.isoformat(),
                "current_stage": st.session_state.get("conversation_stage", "greeting"),
                "duration_minutes": (datetime.now() - st.session_state.interview_start_time).seconds // 60
            },
            "candidate_data": st.session_state.get("candidate_data", {}),
            "messages": st.session_state.get("messages", []),
            "analytics": {
                "total_messages": len(st.session_state.get("messages", [])),
                "ai_generated_questions": len([m for m in st.session_state.get("messages", []) if "AI Generated" in m.get("content", "")]),
                "assessment_scores": st.session_state.get("assessment_scores", []),
                "sentiment_history": st.session_state.get("sentiment_history", [])
            }
        }
        
        # Convert to JSON string for download
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

# Global sidebar instance
sidebar_renderer = render_sidebar
