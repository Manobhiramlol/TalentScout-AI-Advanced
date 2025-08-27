import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Direct imports without using __init__.py
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

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    
    .stChatMessage {
        background-color: rgba(0,0,0,0.02);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .stChatMessage[data-testid="user"] {
        border-left-color: #2196F3;
        background-color: rgba(33, 150, 243, 0.05);
    }
    
    .stChatMessage[data-testid="assistant"] {
        border-left-color: #9C27B0;
        background-color: rgba(156, 39, 176, 0.05);
    }
    
    .stChatInput > div {
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    
    .interview-complete {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_groq_client():
    """Initialize GROQ client with API key from environment or secrets"""
    api_key = os.getenv('GROQ_API_KEY') or st.secrets.get('GROQ_API_KEY', '')
    
    if not api_key:
        st.error("❌ GROQ_API_KEY not found! Please add it to Streamlit secrets.")
        st.info("Go to Settings → Secrets and add: GROQ_API_KEY = 'your_key_here'")
        st.stop()
    
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Failed to initialize GROQ: {str(e)}")
        st.stop()

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'conversation_history': [],
        'current_stage': 'greeting',
        'candidate_info': {},
        'question_count': 0,
        'interview_started': False,
        'interview_start_time': None,
        'assessment_scores': [],
        'sentiment_history': [],
        'ai_response_times': []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def main():
    """Main application function"""
    # Initialize everything
    initialize_session_state()
    client = initialize_groq_client()
    
    # Render sidebar first
    render_sidebar()
    
    # Main content area
    st.markdown("<div class='main-header'>", unsafe_allow_html=True)
    st.title("🎯 TalentScout AI - Advanced Hiring Assistant")
    st.markdown("*AI-powered technical interview chatbot with real-time analytics*")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show interview completion message if completed
    if st.session_state.current_stage == "wrap_up":
        st.markdown("""
        <div class='interview-complete'>
            <h2>🎉 Interview Complete!</h2>
            <p>Thank you for completing the TalentScout AI interview. 
            Your responses have been recorded and our team will review them shortly.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Render main chat interface
    render_chat_interface(client)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p><strong>Built with ❤️ using Streamlit and GROQ AI</strong></p>
            <p>TalentScout AI Advanced v2.0 | Where Intelligence Meets Talent</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
