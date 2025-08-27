"""
Enhanced Advanced Chat Interface with GROQ Integration
Real-time AI interview questions powered by Llama 3.3 70B
"""

import streamlit as st
from datetime import datetime
import time

def render_chat_interface(client):
    """Enhanced chat interface with working GROQ conversation flow"""
    
    st.header("💬 Interview Chat")
    
    # Display conversation history with proper formatting
    display_chat_messages()
    
    # Interview start/continue logic
    if not st.session_state.get('interview_started', False):
        render_start_button(client)
    else:
        # Show dynamic controls during interview
        render_interview_controls(client)
        # Handle user input
        handle_chat_input(client)

def display_chat_messages():
    """Display all chat messages with proper Streamlit components"""
    
    messages = st.session_state.get('conversation_history', [])
    
    if not messages:
        # Welcome message when no conversation exists
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
            👋 **Welcome to TalentScout AI!**
            
            I'm your AI interviewer, powered by **Llama 3.3 70B**. 
            
            I'll conduct a personalized technical interview by:
            - 🎯 Adapting questions to your experience level
            - 💻 Focusing on your declared tech stack  
            - 📊 Providing real-time analytics
            - 🤖 Using advanced AI to generate dynamic questions
            
            Click **Start Interview** when you're ready!
            """)
    else:
        # Display all messages in conversation history
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            
            if role == 'assistant':
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)
            elif role == 'user':
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)

def render_start_button(client):
    """Render the start interview button"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            start_interview(client)
            st.rerun()

def render_interview_controls(client):
    """Render dynamic interview controls"""
    
    if st.session_state.get('current_stage') in ['technical_assessment', 'behavioral_assessment']:
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤖 Generate AI Question", use_container_width=True):
                generate_ai_question(client)
                st.rerun()
        
        with col2:
            if st.button("🔄 Follow-up Question", use_container_width=True):
                generate_followup_question(client)
                st.rerun()
        
        with col3:
            if st.button("⏭️ Next Stage", use_container_width=True):
                advance_interview_stage(client)
                st.rerun()

def start_interview(client):
    """Initialize the interview session"""
    
    st.session_state.interview_started = True
    st.session_state.interview_start_time = datetime.now()
    st.session_state.current_stage = 'greeting'
    st.session_state.question_count = 0
    
    # Initialize conversation history if not exists
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Generate initial greeting using GROQ
    greeting_prompt = """You are a professional AI interviewer for TalentScout, a technology recruitment agency. 

Start the interview with a warm, engaging greeting. Introduce yourself as the TalentScout AI interviewer powered by Llama 3.3 70B. 

Ask for the candidate's name to begin the personalized interview process. Keep it professional but friendly."""
    
    try:
        ai_response = get_groq_response(client, greeting_prompt, [])
        add_message('assistant', ai_response)
        st.session_state.question_count += 1
    except Exception as e:
        st.error(f"Failed to start interview: {str(e)}")

def handle_chat_input(client):
    """Handle user input with proper conversation flow"""
    
    # Get current stage for dynamic placeholder
    stage = st.session_state.get('current_stage', 'greeting')
    placeholder = get_input_placeholder(stage)
    
    # Chat input
    user_input = st.chat_input(placeholder)
    
    if user_input and user_input.strip():
        # Add user message
        add_message('user', user_input)
        
        # Extract candidate information based on stage
        if stage in ['greeting', 'info_collection']:
            extract_candidate_info(user_input)
        
        # Generate AI response
        with st.spinner("🤖 AI is thinking..."):
            try:
                ai_response = generate_contextual_response(client, user_input)
                add_message('assistant', ai_response)
                
                # Update counters and stage
                st.session_state.question_count = st.session_state.get('question_count', 0) + 1
                update_interview_stage()
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

def generate_contextual_response(client, user_input):
    """Generate contextual AI response based on current stage"""
    
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    question_count = st.session_state.get('question_count', 0)
    
    # Build context-aware prompt based on stage
    if stage == 'greeting':
        prompt = f"""The candidate responded: "{user_input}"

Extract their name and move to information collection. Ask for their email address next in a natural, conversational way."""

    elif stage == 'info_collection':
        missing_info = get_missing_info()
        if missing_info:
            next_field = missing_info[0]
            field_prompts = {
                'email': 'their email address',
                'experience': 'their years of professional experience',
                'position': 'what type of position they are interested in',
                'tech_stack': 'their main programming languages and technologies'
            }
            prompt = f"""The candidate responded: "{user_input}"

Current candidate info: {candidate_info}

Ask for {field_prompts.get(next_field, next_field)} next. Be conversational and professional."""
        else:
            # All info collected, transition to technical
            tech_stack = candidate_info.get('tech_stack', 'general programming')
            prompt = f"""All basic information collected: {candidate_info}

Now transition to technical questions. Generate your first technical question based on their tech stack: {tech_stack}

Make it practical and relevant to their experience level."""

    elif stage == 'technical_assessment':
        tech_stack = candidate_info.get('tech_stack', 'programming')
        experience = candidate_info.get('experience', '2-3 years')
        prompt = f"""Candidate's response: "{user_input}"

Background: {experience} experience with {tech_stack}
Questions asked: {question_count}

Generate a follow-up technical question or ask a new one. Focus on practical, real-world scenarios they might encounter."""

    elif stage == 'behavioral_assessment':
        prompt = f"""Candidate's behavioral response: "{user_input}"

Ask a behavioral question using STAR methodology (Situation, Task, Action, Result). Focus on teamwork, problem-solving, or leadership scenarios."""

    else:
        prompt = f"""Continue the interview conversation naturally. Candidate said: "{user_input}" """

    return get_groq_response(client, prompt, st.session_state.conversation_history)

def get_groq_response(client, prompt, conversation_history):
    """Get response from GROQ API"""
    
    try:
        # Prepare messages for GROQ
        messages = [
            {
                "role": "system",
                "content": """You are a professional AI interviewer for TalentScout, powered by Llama 3.3 70B.

Guidelines:
- Be conversational, professional, and engaging
- Ask one question at a time
- Adapt questions based on candidate's background
- Keep responses concise but thorough (2-3 paragraphs max)
- Show genuine interest in their experience
- Use markdown formatting for better readability
- End with a clear, specific question"""
            }
        ]
        
        # Add recent conversation history (last 8 messages)
        for msg in conversation_history[-8:]:
            if msg.get('role') and msg.get('content'):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Make GROQ API call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, I'm experiencing technical difficulties. Error: {str(e)}. Please try again."

def generate_ai_question(client):
    """Generate a new AI question based on candidate background"""
    
    candidate_info = st.session_state.get('candidate_info', {})
    stage = st.session_state.get('current_stage', 'technical_assessment')
    
    if stage == 'technical_assessment':
        tech_stack = candidate_info.get('tech_stack', 'programming')
        experience = candidate_info.get('experience', '2-3 years')
        
        prompt = f"""Generate a technical interview question for someone with {experience} experience in {tech_stack}.

Make it:
- Practical and scenario-based
- Relevant to real-world development
- Appropriate for their experience level
- Different from previous questions asked

Format as a clear, engaging question."""
        
        response = get_groq_response(client, prompt, [])
        add_message('assistant', f"🤖 **AI-Generated Question:**\n\n{response}")
    
    elif stage == 'behavioral_assessment':
        prompt = """Generate a behavioral interview question focusing on soft skills.

Use STAR methodology and focus on one of these areas:
- Teamwork and collaboration
- Problem-solving under pressure  
- Leadership and initiative
- Adapting to change
- Communication challenges

Make it specific and scenario-based."""
        
        response = get_groq_response(client, prompt, [])
        add_message('assistant', f"🎯 **Behavioral Question:**\n\n{response}")

def generate_followup_question(client):
    """Generate a follow-up question based on last response"""
    
    messages = st.session_state.get('conversation_history', [])
    user_messages = [m for m in messages if m['role'] == 'user']
    
    if user_messages:
        last_response = user_messages[-1]['content']
        
        prompt = f"""The candidate just said: "{last_response}"

Generate a thoughtful follow-up question that:
- Digs deeper into their approach
- Explores alternatives they considered
- Understands their decision-making process
- Shows interest in their technical reasoning

Make it conversational and engaging."""
        
        response = get_groq_response(client, prompt, [])
        add_message('assistant', f"🔄 **Follow-up:**\n\n{response}")

def advance_interview_stage(client):
    """Advance to the next interview stage"""
    
    current_stage = st.session_state.get('current_stage', 'greeting')
    
    stage_progression = {
        'greeting': 'info_collection',
        'info_collection': 'technical_assessment',
        'technical_assessment': 'behavioral_assessment',
        'behavioral_assessment': 'wrap_up'
    }
    
    next_stage = stage_progression.get(current_stage, 'wrap_up')
    st.session_state.current_stage = next_stage
    
    # Generate transition message
    transition_messages = {
        'info_collection': "📝 **Information Collection Phase**\n\nLet's gather some details about your background.",
        'technical_assessment': "💻 **Technical Assessment**\n\nNow I'll ask some technical questions based on your skills.",
        'behavioral_assessment': "🤝 **Behavioral Assessment**\n\nLet's discuss some soft skills and work scenarios.",
        'wrap_up': generate_interview_summary()
    }
    
    message = transition_messages.get(next_stage, "Moving to the next stage...")
    add_message('assistant', message)

def generate_interview_summary():
    """Generate interview completion summary"""
    
    candidate_info = st.session_state.get('candidate_info', {})
    question_count = st.session_state.get('question_count', 0)
    duration = calculate_duration()
    
    name = candidate_info.get('name', 'there')
    
    return f"""🎉 **Interview Complete!**

Thank you for your time today, **{name}**!

**📊 Interview Summary:**
- **Questions Asked:** {question_count}
- **Duration:** {duration}
- **Stages Completed:** All phases ✅

**🚀 Next Steps:**
1. Our team will review your responses
2. You'll hear back within 2-3 business days
3. Prepare for potential technical deep-dive

**💡 Key Highlights:**
- Demonstrated strong technical knowledge
- Great communication skills
- Professional throughout the process

Have a wonderful day! 🌟"""

# Helper functions
def add_message(role, content):
    """Add message to conversation history"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    st.session_state.conversation_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now()
    })

def extract_candidate_info(user_input):
    """Extract candidate information from responses"""
    
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    
    candidate_info = st.session_state.candidate_info
    user_lower = user_input.lower()
    
    # Extract name (simple approach)
    if 'name' not in candidate_info and any(phrase in user_lower for phrase in ['my name is', 'i am', "i'm"]):
        words = user_input.split()
        for i, word in enumerate(words):
            if word.lower() in ['am', 'is'] and i + 1 < len(words):
                candidate_info['name'] = ' '.join(words[i+1:i+3]).strip('.,!?')
                break
    
    # Extract email
    if 'email' not in candidate_info and '@' in user_input:
        import re
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        if email_match:
            candidate_info['email'] = email_match.group()
    
    # Extract experience
    if 'experience' not in candidate_info:
        import re
        patterns = [r'(\d+)\s*year', r'(\d+)\s*yr', r'over\s*(\d+)', r'about\s*(\d+)']
        for pattern in patterns:
            match = re.search(pattern, user_lower)
            if match:
                candidate_info['experience'] = f"{match.group(1)} years"
                break
    
    # Extract tech stack
    if any(word in user_lower for word in ['python', 'javascript', 'java', 'react', 'node', 'sql']):
        tech_terms = ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'mongodb', 'aws', 'docker', 'git']
        found_tech = [term for term in tech_terms if term in user_lower]
        if found_tech and 'tech_stack' not in candidate_info:
            candidate_info['tech_stack'] = ', '.join(found_tech).title()

def get_missing_info():
    """Get list of missing required information"""
    candidate_info = st.session_state.get('candidate_info', {})
    required = ['name', 'email', 'experience', 'position', 'tech_stack']
    return [field for field in required if field not in candidate_info or not candidate_info[field]]

def update_interview_stage():
    """Update interview stage based on progress"""
    candidate_info = st.session_state.get('candidate_info', {})
    question_count = st.session_state.get('question_count', 0)
    current_stage = st.session_state.get('current_stage', 'greeting')
    
    # Auto-advance logic
    if current_stage == 'greeting' and len(st.session_state.get('conversation_history', [])) >= 4:
        st.session_state.current_stage = 'info_collection'
    elif current_stage == 'info_collection' and len(get_missing_info()) == 0:
        st.session_state.current_stage = 'technical_assessment'
    elif current_stage == 'technical_assessment' and question_count >= 8:
        st.session_state.current_stage = 'behavioral_assessment'
    elif current_stage == 'behavioral_assessment' and question_count >= 12:
        st.session_state.current_stage = 'wrap_up'

def get_input_placeholder(stage):
    """Get placeholder text for input based on stage"""
    placeholders = {
        'greeting': "What's your name?",
        'info_collection': "Enter your response...",
        'technical_assessment': "Describe your technical approach...",
        'behavioral_assessment': "Use STAR method (Situation, Task, Action, Result)...",
        'wrap_up': "Any final questions or comments?"
    }
    return placeholders.get(stage, "Type your response...")

def calculate_duration():
    """Calculate interview duration"""
    start_time = st.session_state.get('interview_start_time')
    if start_time:
        duration = datetime.now() - start_time
        minutes = duration.seconds // 60
        return f"{minutes} minutes"
    return "0 minutes"
