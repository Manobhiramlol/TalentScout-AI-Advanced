import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="TalentScout AI - Advanced Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
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
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .interview-stage {
        background-color: #e8f5e8;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        color: #2e7d32;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .status-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-active { background-color: #d4edda; color: #155724; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-completed { background-color: #cce5ff; color: #004085; }
</style>
""", unsafe_allow_html=True)

# Initialize GROQ client
@st.cache_resource
def initialize_groq_client():
    """Initialize GROQ client with API key from environment or secrets"""
    api_key = os.getenv('GROQ_API_KEY') or st.secrets.get('GROQ_API_KEY', '')
    
    if not api_key:
        st.error("❌ GROQ_API_KEY not found! Please add it to Streamlit secrets.")
        st.info("Go to Settings → Secrets and add: GROQ_API_KEY = 'your_key_here'")
        st.stop()
    
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize GROQ client: {str(e)}")
        st.stop()

# Initialize session state with analytics data
def initialize_session_state():
    """Initialize all session state variables including analytics"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'greeting'
    
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0
    
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
    if 'interview_start_time' not in st.session_state:
        st.session_state.interview_start_time = None
    
    if 'response_times' not in st.session_state:
        st.session_state.response_times = []
    
    if 'sentiment_scores' not in st.session_state:
        st.session_state.sentiment_scores = []
    
    if 'technical_topics' not in st.session_state:
        st.session_state.technical_topics = []

# Analytics functions
def analyze_response_sentiment(text):
    """Simple sentiment analysis (you can enhance with actual NLP)"""
    positive_words = ['good', 'great', 'excellent', 'love', 'enjoy', 'excited', 'confident', 'yes']
    negative_words = ['bad', 'terrible', 'hate', 'difficult', 'no', 'never', 'worried', 'concerned']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 0.7 + (positive_count * 0.1)
    elif negative_count > positive_count:
        return 0.3 - (negative_count * 0.1)
    else:
        return 0.5

def calculate_engagement_score():
    """Calculate engagement based on response length and frequency"""
    if not st.session_state.conversation_history:
        return 0
    
    user_responses = [msg for msg in st.session_state.conversation_history if msg['role'] == 'user']
    if not user_responses:
        return 0
    
    avg_length = sum(len(msg['content']) for msg in user_responses) / len(user_responses)
    
    # Normalize to 0-100 scale
    engagement = min(100, (avg_length / 50) * 100)
    return round(engagement, 1)

def extract_technical_skills():
    """Extract mentioned technical skills from conversation"""
    tech_keywords = ['python', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'aws', 'docker', 
                    'kubernetes', 'git', 'api', 'frontend', 'backend', 'database', 'cloud']
    
    mentioned_skills = set()
    for msg in st.session_state.conversation_history:
        if msg['role'] == 'user':
            text_lower = msg['content'].lower()
            for skill in tech_keywords:
                if skill in text_lower:
                    mentioned_skills.add(skill.title())
    
    return list(mentioned_skills)

# GROQ API call function (same as before)
def get_ai_response(client, prompt, conversation_history=[]):
    """Generate AI response using GROQ API"""
    try:
        messages = [
            {
                "role": "system",
                "content": """You are a professional AI interviewer for TalentScout, a technology recruitment agency. 
                Your role is to conduct technical interviews in a friendly, professional manner.
                
                Guidelines:
                - Be conversational and welcoming
                - Ask one question at a time
                - Focus on practical skills and experience
                - Adapt questions based on candidate responses
                - Keep questions relevant to their declared tech stack
                """
            }
        ]
        
        for msg in conversation_history[-10:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"❌ Question generation failed: {str(e)}")
        return "I apologize, but I'm having trouble generating a response. Please try again."

# Dashboard components
def render_real_time_analytics():
    """Render real-time analytics dashboard"""
    st.header("📊 Real-Time Interview Analytics")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Interview Progress",
            value=f"{st.session_state.question_count}",
            delta="Questions Asked"
        )
    
    with col2:
        engagement = calculate_engagement_score()
        st.metric(
            label="📈 Engagement Score",
            value=f"{engagement}%",
            delta="Response Quality"
        )
    
    with col3:
        if st.session_state.interview_start_time:
            duration = (datetime.now() - st.session_state.interview_start_time).seconds // 60
            st.metric(
                label="⏱️ Duration",
                value=f"{duration} min",
                delta="Time Elapsed"
            )
        else:
            st.metric(label="⏱️ Duration", value="0 min")
    
    with col4:
        technical_skills = extract_technical_skills()
        st.metric(
            label="💻 Tech Skills",
            value=f"{len(technical_skills)}",
            delta="Skills Mentioned"
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment trend
        if st.session_state.sentiment_scores:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=st.session_state.sentiment_scores,
                mode='lines+markers',
                name='Sentiment Score',
                line=dict(color='#2E86AB', width=3)
            ))
            fig.update_layout(
                title="📈 Sentiment Trend",
                yaxis_title="Sentiment Score",
                xaxis_title="Response Number",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📈 Sentiment analysis will appear after responses")
    
    with col2:
        # Response time analysis
        if st.session_state.response_times:
            fig = px.bar(
                x=list(range(1, len(st.session_state.response_times) + 1)),
                y=st.session_state.response_times,
                title="⏰ Response Time Analysis",
                labels={'x': 'Response Number', 'y': 'Time (seconds)'}
            )
            fig.update_traces(marker_color='#A23B72')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⏰ Response time tracking will appear during interview")
    
    # Technical skills radar chart
    if technical_skills:
        st.subheader("💻 Technical Skills Mentioned")
        skills_df = pd.DataFrame({
            'Skill': technical_skills,
            'Mentioned': [1] * len(technical_skills)
        })
        
        fig = px.bar(
            skills_df, 
            x='Skill', 
            y='Mentioned',
            title="Technical Skills Coverage"
        )
        fig.update_traces(marker_color='#F18F01')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_candidate_dashboard():
    """Render candidate information dashboard"""
    st.header("👤 Candidate Profile Dashboard")
    
    if not st.session_state.candidate_info:
        st.info("📝 Candidate information will appear as the interview progresses")
        return
    
    # Candidate info cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Basic Information")
        info_data = []
        
        field_icons = {
            'name': '👤',
            'email': '📧',
            'experience': '⏰',
            'position': '🎯',
            'tech_stack': '💻'
        }
        
        for key, value in st.session_state.candidate_info.items():
            if value:
                icon = field_icons.get(key, '📌')
                info_data.append({
                    'Field': f"{icon} {key.replace('_', ' ').title()}",
                    'Value': str(value)
                })
        
        if info_data:
            df = pd.DataFrame(info_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Interview Status")
        
        # Current stage with visual indicator
        stage_status = {
            'greeting': ('👋', 'Greeting', 'completed' if st.session_state.current_stage != 'greeting' else 'active'),
            'info_collection': ('📝', 'Info Collection', 'completed' if st.session_state.current_stage not in ['greeting', 'info_collection'] else 'active' if st.session_state.current_stage == 'info_collection' else 'pending'),
            'technical_assessment': ('💻', 'Technical Assessment', 'completed' if st.session_state.current_stage == 'wrap_up' else 'active' if st.session_state.current_stage == 'technical_assessment' else 'pending'),
            'wrap_up': ('✅', 'Wrap Up', 'active' if st.session_state.current_stage == 'wrap_up' else 'pending')
        }
        
        for stage, (icon, name, status) in stage_status.items():
            status_class = f"status-{status}"
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                <span style="flex-grow: 1;">{name}</span>
                <span class="status-badge {status_class}">{status.title()}</span>
            </div>
            """, unsafe_allow_html=True)

def render_interview_summary():
    """Render interview summary and recommendations"""
    st.header("📋 Interview Summary & Recommendations")
    
    if not st.session_state.conversation_history:
        st.info("📊 Interview summary will be generated after the conversation begins")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_responses = len([msg for msg in st.session_state.conversation_history if msg['role'] == 'user'])
        st.metric("💬 Total Responses", total_responses)
    
    with col2:
        avg_response_length = 0
        user_responses = [msg for msg in st.session_state.conversation_history if msg['role'] == 'user']
        if user_responses:
            avg_response_length = sum(len(msg['content']) for msg in user_responses) // len(user_responses)
        st.metric("📝 Avg Response Length", f"{avg_response_length} chars")
    
    with col3:
        technical_skills = extract_technical_skills()
        st.metric("🔧 Technical Skills", len(technical_skills))
    
    # Recommendations
    st.subheader("🎯 AI Recommendations")
    
    recommendations = []
    
    if calculate_engagement_score() > 70:
        recommendations.append("✅ **High Engagement**: Candidate shows strong communication skills")
    elif calculate_engagement_score() < 30:
        recommendations.append("⚠️ **Low Engagement**: Consider follow-up questions to encourage detailed responses")
    
    if len(technical_skills) > 5:
        recommendations.append("✅ **Strong Technical Background**: Candidate demonstrates diverse technical knowledge")
    elif len(technical_skills) < 3:
        recommendations.append("⚠️ **Limited Technical Discussion**: Consider more technical deep-dive questions")
    
    if st.session_state.question_count > 8:
        recommendations.append("📊 **Comprehensive Interview**: Good coverage of topics")
    else:
        recommendations.append("📝 **Interview In Progress**: Continue with more questions for better assessment")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # Export functionality
    if st.button("📥 Export Interview Report"):
        report_data = {
            'candidate_info': st.session_state.candidate_info,
            'conversation_history': st.session_state.conversation_history,
            'analytics': {
                'engagement_score': calculate_engagement_score(),
                'technical_skills': technical_skills,
                'total_questions': st.session_state.question_count,
                'interview_duration': (datetime.now() - st.session_state.interview_start_time).seconds // 60 if st.session_state.interview_start_time else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        st.download_button(
            label="💾 Download JSON Report",
            data=json.dumps(report_data, indent=2),
            file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Main app with full dashboard
def main():
    initialize_session_state()
    client = initialize_groq_client()
    
    # Header
    st.markdown("<div class='main-header'>", unsafe_allow_html=True)
    st.title("🎯 TalentScout AI - Advanced Hiring Assistant")
    st.markdown("*AI-powered technical interview chatbot with real-time analytics*")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Interview Chat", "📊 Real-Time Analytics", "👤 Candidate Dashboard"])
    
    with tab1:
        # Interview chat interface (same as before)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("💬 Interview Chat")
            
            # Display conversation history
            for message in st.session_state.conversation_history:
                role = message['role']
                content = message['content']
                
                if role == 'assistant':
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 TalentScout AI:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Start interview button
            if not st.session_state.interview_started:
                if st.button("🚀 Start Interview", type="primary", use_container_width=True):
                    st.session_state.interview_started = True
                    st.session_state.interview_start_time = datetime.now()
                    
                    # Generate initial greeting
                    ai_response = get_ai_response(client, "Start the interview with a warm greeting.", [])
                    
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                    st.session_state.question_count += 1
                    st.rerun()
            
            # Chat input
            if st.session_state.interview_started:
                user_input = st.chat_input("Type your response here...")
                
                if user_input:
                    response_start_time = time.time()
                    
                    # Add user message
                    st.session_state.conversation_history.append({
                        'role': 'user',
                        'content': user_input
                    })
                    
                    # Analyze response
                    sentiment = analyze_response_sentiment(user_input)
                    st.session_state.sentiment_scores.append(sentiment)
                    
                    # Record response time
                    response_time = time.time() - response_start_time
                    st.session_state.response_times.append(response_time)
                    
                    # Generate AI response
                    ai_response = get_ai_response(client, "Continue the interview naturally.", st.session_state.conversation_history)
                    
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                    st.session_state.question_count += 1
                    st.rerun()
        
        with col2:
            # Quick stats sidebar
            st.subheader("📈 Quick Stats")
            
            if st.session_state.interview_started:
                st.metric("Questions", st.session_state.question_count)
                st.metric("Engagement", f"{calculate_engagement_score()}%")
                
                if st.session_state.interview_start_time:
                    duration = (datetime.now() - st.session_state.interview_start_time).seconds // 60
                    st.metric("Duration", f"{duration} min")
                
                # Reset button
                if st.button("🔄 Reset Interview"):
                    for key in ['conversation_history', 'current_stage', 'candidate_info', 'question_count', 'interview_started', 'interview_start_time', 'response_times', 'sentiment_scores']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
    
    with tab2:
        render_real_time_analytics()
    
    with tab3:
        render_candidate_dashboard()
        st.markdown("---")
        render_interview_summary()
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with ❤️ using Streamlit and GROQ AI | TalentScout AI v2.0*")

if __name__ == "__main__":
    main()
