import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import time

# Import components
from components.sidebar import render_sidebar
from components.advanced_chat import render_chat_interface

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="TalentScout AI - Advanced Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    
    .ai-status-online {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .ai-status-offline {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_groq_client():
    """Initialize GROQ client with status checking"""
    api_key = os.getenv('GROQ_API_KEY') or st.secrets.get('GROQ_API_KEY', '')
    
    if not api_key:
        st.session_state.ai_status = "No API Key"
        st.error("❌ GROQ_API_KEY not found!")
        st.stop()
    
    try:
        client = Groq(api_key=api_key)
        # Test the connection
        test_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        st.session_state.ai_status = "Online"
        st.session_state.ai_model = "llama-3.3-70b-versatile"
        return client
    except Exception as e:
        st.session_state.ai_status = f"Error: {str(e)}"
        st.error(f"❌ GROQ Connection Failed: {str(e)}")
        st.stop()

def initialize_session_state():
    """Initialize comprehensive session state"""
    defaults = {
        'conversation_history': [],
        'current_stage': 'greeting',
        'candidate_info': {},
        'question_count': 0,
        'interview_started': False,
        'interview_start_time': None,
        'ai_status': 'Checking...',
        'ai_model': '',
        'response_times': [],
        'sentiment_scores': [],
        'quality_metrics': [],
        'session_analytics': {
            'total_questions': 0,
            'avg_response_length': 0,
            'engagement_score': 0,
            'technical_skills_mentioned': 0
        }
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_ai_status():
    """Real-time AI status indicator"""
    status = st.session_state.get('ai_status', 'Unknown')
    if status == "Online":
        return "🟢 AI Model Online"
    elif "Error" in status:
        return f"🔴 AI Error: {status}"
    else:
        return f"🟡 AI Status: {status}"

def render_ai_dashboard():
    """Comprehensive AI Analytics Dashboard"""
    st.header("🤖 AI Performance Dashboard")
    
    # AI Status Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🤖 AI Status", 
            value=st.session_state.get('ai_status', 'Unknown'),
            delta="Llama 3.3 70B"
        )
    
    with col2:
        questions_generated = len([m for m in st.session_state.conversation_history 
                                 if m.get('role') == 'assistant' and len(m.get('content', '')) > 100])
        st.metric(
            label="🧠 AI Questions Generated", 
            value=questions_generated,
            delta="Dynamic Generation"
        )
    
    with col3:
        avg_response_time = sum(st.session_state.response_times) / len(st.session_state.response_times) if st.session_state.response_times else 0
        st.metric(
            label="⚡ Avg Response Time", 
            value=f"{avg_response_time:.2f}s",
            delta="Real-time"
        )
    
    with col4:
        model_efficiency = (questions_generated / max(len(st.session_state.conversation_history), 1)) * 100
        st.metric(
            label="🎯 AI Efficiency", 
            value=f"{model_efficiency:.0f}%",
            delta="Performance"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.response_times and len(st.session_state.response_times) > 1:
            st.subheader("⏱️ Response Time Trend")
            fig = px.line(
                x=list(range(len(st.session_state.response_times))),
                y=st.session_state.response_times,
                title="AI Response Times Over Session"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Response time data will appear after AI interactions")
    
    with col2:
        if st.session_state.sentiment_scores and len(st.session_state.sentiment_scores) > 1:
            st.subheader("😊 Candidate Sentiment Analysis")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=st.session_state.sentiment_scores,
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color='#2E86AB', width=3)
            ))
            fig.update_layout(
                title="Sentiment Trend During Interview",
                yaxis_title="Sentiment Score",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sentiment analysis will appear after candidate responses")

def render_interview_analytics():
    """Comprehensive Interview Analytics"""
    st.header("📊 Interview Analytics Dashboard")
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_duration = 0
        if st.session_state.interview_start_time:
            total_duration = (datetime.now() - st.session_state.interview_start_time).seconds // 60
        st.metric("⏱️ Interview Duration", f"{total_duration} minutes")
    
    with col2:
        user_responses = len([m for m in st.session_state.conversation_history if m.get('role') == 'user'])
        st.metric("💬 Candidate Responses", user_responses)
    
    with col3:
        engagement = calculate_engagement_score()
        st.metric("📈 Engagement Score", f"{engagement}%")
    
    with col4:
        completion = calculate_interview_completion()
        st.metric("✅ Interview Progress", f"{completion}%")
    
    # Analytics Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Response Length Distribution
        if st.session_state.conversation_history:
            user_msgs = [m for m in st.session_state.conversation_history if m.get('role') == 'user']
            if user_msgs:
                lengths = [len(m.get('content', '').split()) for m in user_msgs]
                fig = px.histogram(
                    x=lengths,
                    title="Response Length Distribution",
                    labels={'x': 'Words per Response', 'y': 'Frequency'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Interview Stage Progress
        stages = ['Greeting', 'Info Collection', 'Technical', 'Behavioral', 'Wrap-up']
        current_stage = st.session_state.current_stage
        progress_data = [1 if stage.lower().replace(' ', '_') == current_stage else 0 for stage in stages]
        
        fig = px.bar(
            x=stages,
            y=progress_data,
            title="Interview Stage Progress"
        )
        st.plotly_chart(fig, use_container_width=True)

def render_candidate_insights():
    """Advanced Candidate Analysis"""
    st.header("👤 Candidate Insights & Recommendations")
    
    candidate_info = st.session_state.candidate_info
    
    if not candidate_info:
        st.info("🔍 Candidate insights will appear as information is collected during the interview.")
        return
    
    # Candidate Summary Card
    st.subheader("📋 Candidate Profile Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profile completeness
        required_fields = ['name', 'email', 'experience', 'position', 'tech_stack']
        completed = sum(1 for field in required_fields if candidate_info.get(field))
        completeness = (completed / len(required_fields)) * 100
        
        st.metric("📊 Profile Completeness", f"{completeness:.0f}%")
        
        # Skills Analysis
        tech_stack = candidate_info.get('tech_stack', '')
        if tech_stack:
            skills = [skill.strip() for skill in tech_stack.split(',')]
            st.metric("💻 Technical Skills", len(skills))
            
            # Skills breakdown
            st.write("**Technical Skills:**")
            for skill in skills[:5]:  # Show top 5 skills
                st.write(f"• {skill}")
    
    with col2:
        # Experience Analysis
        experience = candidate_info.get('experience', '0')
        st.metric("⏰ Experience Level", experience)
        
        # Position Match
        position = candidate_info.get('position', 'Not specified')
        st.metric("🎯 Target Position", position)
        
        # AI Recommendations
        st.write("**AI Recommendations:**")
        recommendations = generate_ai_recommendations(candidate_info)
        for rec in recommendations:
            st.write(f"✅ {rec}")

def generate_ai_recommendations(candidate_info):
    """Generate AI-powered recommendations"""
    recommendations = []
    
    experience = candidate_info.get('experience', '0')
    tech_stack = candidate_info.get('tech_stack', '')
    
    if 'python' in tech_stack.lower():
        recommendations.append("Strong Python background - suitable for backend roles")
    
    if any(word in tech_stack.lower() for word in ['react', 'javascript', 'frontend']):
        recommendations.append("Frontend skills detected - consider full-stack positions")
    
    if '5+' in experience or 'senior' in experience.lower():
        recommendations.append("Senior-level candidate - ready for leadership roles")
    
    return recommendations or ["Continue gathering information for personalized recommendations"]

def calculate_engagement_score():
    """Calculate candidate engagement score"""
    user_messages = [m for m in st.session_state.conversation_history if m.get('role') == 'user']
    if not user_messages:
        return 0
    
    avg_length = sum(len(m.get('content', '')) for m in user_messages) / len(user_messages)
    engagement = min(100, (avg_length / 100) * 100)
    return round(engagement, 1)

def calculate_interview_completion():
    """Calculate interview completion percentage"""
    stage_progress = {
        'greeting': 20,
        'info_collection': 40,
        'technical_assessment': 70,
        'behavioral_assessment': 90,
        'wrap_up': 100
    }
    return stage_progress.get(st.session_state.current_stage, 10)

def main():
    """Enhanced main application"""
    # Initialize everything
    initialize_session_state()
    client = initialize_groq_client()
    
    # Render sidebar with all analytics
    render_sidebar()
    
    # Main header with AI status
    st.markdown(f"""
    <div class='main-header'>
        <h1>🎯 TalentScout AI - Advanced Hiring Assistant</h1>
        <p><strong>AI-powered technical interviews with real-time analytics</strong></p>
        <p>{check_ai_status()} | Model: {st.session_state.ai_model}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-tab interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Interview Chat", 
        "🤖 AI Dashboard", 
        "📊 Analytics", 
        "👤 Candidate Insights"
    ])
    
    with tab1:
        render_chat_interface(client)
    
    with tab2:
        render_ai_dashboard()
    
    with tab3:
        render_interview_analytics()
    
    with tab4:
        render_candidate_insights()
    
    # Enhanced footer with system status
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666;'>
        <p><strong>TalentScout AI Advanced v2.0</strong> | 
        🤖 {st.session_state.ai_status} | 
        ⚡ Real-time Analytics | 
        🔒 Enterprise Security</p>
        <p>Built with ❤️ using Streamlit, GROQ AI, and Plotly | 
        Last Updated: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
