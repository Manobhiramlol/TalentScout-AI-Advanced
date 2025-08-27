import streamlit as st
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv
import nest_asyncio

# CRITICAL: Apply nest_asyncio for Streamlit compatibility
nest_asyncio.apply()

# Load environment variables first
load_dotenv()

# Enhanced API key check with debugging
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found! Please add it to your .env file.")
    st.info("Expected format: GROQ_API_KEY=gsk_your_key_here")
    st.stop()

# Initialize managers with error handling
try:
    from core.ai_manager import AdvancedAIManager
    ai_manager = AdvancedAIManager()
    
except Exception as e:
    st.error(f"Manager initialization failed: {e}")
    st.stop()

def initialize_app():
    """Initialize application and session state"""
    
    # Page config
    st.set_page_config(
        page_title="TalentScout AI Advanced",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(datetime.now().timestamp())}"
    
    if "conversation_stage" not in st.session_state:
        st.session_state.conversation_stage = "greeting"
    
    # CRITICAL: Initialize messages list
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AI manager in session state
    if "ai_manager" not in st.session_state:
        st.session_state.ai_manager = ai_manager
    
    return True

def initialize_chat_flow():
    """Initialize chat conversation flow with initial greeting"""
    
    # Add initial AI greeting if no messages exist
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "assistant",
            "content": """Hello! 👋 Welcome to **TalentScout AI Advanced**.

I'm your AI interviewer, powered by Llama 3.3 70B with advanced prompt engineering. I'm excited to learn about your background and skills through an intelligent, adaptive conversation.

Let's start with your name - what should I call you?""",
            "timestamp": datetime.now(),
            "stage": "greeting",
            "message_id": 1
        })

def main():
    """Main application function"""
    
    # Initialize app first
    if not initialize_app():
        st.stop()
    
    # CRITICAL: Initialize chat flow after app initialization
    initialize_chat_flow()
    
    # Show API key status in sidebar
    with st.sidebar:
        st.success(f"✅ API Key: {groq_api_key[:8]}...")
        
        # Test AI connection button
        if st.button("🧪 Test AI Connection"):
            try:
                test_response = ai_manager.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "Hello! Test connection."}],
                    max_tokens=50
                )
                st.success(f"✅ AI Test: {test_response.choices[0].message.content}")
                st.info("API connection successful! You can now use dynamic question generation.")
            except Exception as e:
                st.error(f"❌ AI Test Failed: {e}")
                st.error("Please check your API key and internet connection.")
    
    # Header
    st.title("🎯 TalentScout AI Advanced")
    st.markdown("*Enterprise AI-Powered Hiring Assistant*")
    
    # Enhanced system status with debugging
    with st.expander("🔧 System Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success("✅ GROQ API Key: Loaded")
            st.caption(f"Key: {groq_api_key[:8]}...")
        with col2:
            st.success(f"✅ Database: Ready")
        with col3:
            st.success("✅ AI Manager: Ready")
            st.caption(f"Messages: {len(st.session_state.messages)}")
        
        # Show session state debug
        st.write("**Session Debug:**")
        st.write(f"- Messages initialized: {'✅' if 'messages' in st.session_state else '❌'}")
        st.write(f"- Message count: {len(st.session_state.get('messages', []))}")
        st.write(f"- Conversation stage: {st.session_state.get('conversation_stage', 'None')}")
        st.write(f"- AI Manager loaded: {'✅' if st.session_state.get('ai_manager') else '❌'}")
    
    # Navigation
    tab1, tab2, tab3 = st.tabs(["💬 Interview", "📊 Dashboard", "📈 Analytics"])
    
    with tab1:
        # Main interview interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            from components.advanced_chat import render_chat_interface
            render_chat_interface()
        
        with col2:
            from components.sidebar import render_sidebar
            render_sidebar()
    
    with tab2:
        st.info("👆 Dashboard features available in full version")
    
    with tab3:
        st.info("📈 Analytics features available in full version")
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by TalentScout AI Advanced v2.0*")

if __name__ == "__main__":
    main()
