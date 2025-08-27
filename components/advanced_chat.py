"""
Enhanced Advanced Chat Interface with Dynamic Controls
Includes: Generate Next Question, Skip Stage, Follow-up Question
"""

import streamlit as st
from datetime import datetime
import re

def render_chat_interface(client):
    """Enhanced chat interface with dynamic controls"""
    
    st.header("💬 Interview Chat")
    
    # Display conversation history
    display_chat_messages()
    
    # Interview controls
    if not st.session_state.get('interview_started', False):
        render_start_button(client)
    else:
        # Show current stage info and dynamic controls
        render_stage_info_and_controls(client)
        # Handle user input
        handle_chat_input(client)

def display_chat_messages():
    """Display all chat messages properly"""
    messages = st.session_state.get('conversation_history', [])
    
    if not messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
            👋 **Welcome to TalentScout AI!**
            
            I'm your AI interviewer, powered by **Llama 3.3 70B**. I'll conduct a structured technical interview by:
            - 🎯 Collecting your basic information
            - 💻 Asking technical questions based on your skills
            - 🧠 Evaluating your problem-solving approach
            - 📊 Providing real-time analytics
            
            Click **Start Interview** when you're ready!
            """)
    else:
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            
            if role == 'assistant':
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)
            elif role == 'user':
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)

def render_stage_info_and_controls(client):
    """Show current stage and dynamic interview controls"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    # Stage information
    stage_messages = {
        'greeting': "👋 **Current Stage:** Initial Greeting",
        'info_collection': f"📝 **Current Stage:** Information Collection (Collected: {len(candidate_info)} items)",
        'technical_assessment': "💻 **Current Stage:** Technical Assessment",
        'behavioral_assessment': "🧠 **Current Stage:** Behavioral Assessment", 
        'wrap_up': "✅ **Current Stage:** Interview Complete"
    }
    
    st.info(stage_messages.get(stage, "Interview in progress..."))
    
    # Dynamic Controls Section
    if stage in ['technical_assessment', 'behavioral_assessment']:
        st.markdown("---")
        st.subheader("🎛️ Interview Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤖 Generate Next Question", use_container_width=True, type="primary"):
                generate_ai_question(client)
                st.rerun()
        
        with col2:
            if st.button("🔄 Follow-up Question", use_container_width=True, type="secondary"):
                generate_followup_question(client)
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip to Next Stage", use_container_width=True, type="secondary"):
                skip_to_next_stage(client)
                st.rerun()
        
        # Additional controls row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Custom Question", use_container_width=True):
                render_custom_question_input(client)
        
        with col2:
            if st.button("📊 Generate Summary", use_container_width=True):
                generate_interview_summary(client)
                st.rerun()
        
        with col3:
            if st.button("🔄 Repeat Question", use_container_width=True):
                repeat_last_question()
                st.rerun()

def render_custom_question_input(client):
    """Render custom question input form"""
    with st.form("custom_question_form"):
        st.write("**✏️ Ask a Custom Question:**")
        custom_question = st.text_area(
            "Enter your custom question:",
            placeholder="e.g., Can you explain your experience with cloud technologies?",
            height=100
        )
        
        submitted = st.form_submit_button("Ask Question", type="primary")
        
        if submitted and custom_question.strip():
            add_message('assistant', f"**Custom Question:**\n\n{custom_question.strip()}")
            st.session_state.question_count = st.session_state.get('question_count', 0) + 1
            st.success("✅ Custom question added to the interview!")
            st.rerun()

def render_start_button(client):
    """Render start interview button"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            start_interview(client)
            st.rerun()

def start_interview(client):
    """Initialize interview with proper greeting"""
    st.session_state.interview_started = True
    st.session_state.interview_start_time = datetime.now()
    st.session_state.current_stage = 'greeting'
    st.session_state.question_count = 0
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Generate initial greeting
    greeting = """Hello! I'm your AI interviewer from TalentScout. I'm here to conduct a comprehensive technical interview tailored to your background.

Let's start with the basics. **What's your full name?**"""
    
    add_message('assistant', greeting)
    st.session_state.question_count += 1

def generate_ai_question(client):
    """Generate a new AI question based on candidate background"""
    try:
        candidate_info = st.session_state.get('candidate_info', {})
        stage = st.session_state.get('current_stage', 'technical_assessment')
        
        with st.spinner("🧠 AI is generating a personalized question..."):
            if stage == 'technical_assessment':
                tech_stack = candidate_info.get('tech_stack', 'programming')
                experience = candidate_info.get('experience', '2-3 years')
                position = candidate_info.get('position', 'Software Engineer')
                
                prompt = f"""You are a professional technical interviewer. Generate a challenging and insightful technical interview question for a {position} with {experience} experience in {tech_stack}.

Requirements:
- Make it practical and scenario-based
- Focus on real-world problem-solving
- Appropriate for their experience level
- Different from typical generic questions
- Should test both technical knowledge and thinking process

Format: Return only the question, make it engaging and specific."""
                
                ai_question = get_groq_response(client, prompt, [])
                add_message('assistant', f"🤖 **AI Generated Technical Question:**\n\n{ai_question}")
                
            elif stage == 'behavioral_assessment':
                position = candidate_info.get('position', 'Software Engineer')
                
                prompt = f"""Generate a behavioral interview question for a {position} that explores soft skills and work approach.

Focus on one of these areas:
- Leadership and initiative
- Problem-solving under pressure
- Team collaboration and conflict resolution
- Adapting to change and learning
- Communication with stakeholders

Use STAR methodology and make it specific to their role. Return only the question."""
                
                ai_question = get_groq_response(client, prompt, [])
                add_message('assistant', f"🎯 **AI Generated Behavioral Question:**\n\n{ai_question}")
        
        st.session_state.question_count = st.session_state.get('question_count', 0) + 1
        st.success("✨ New AI question generated!")
        
    except Exception as e:
        st.error(f"Failed to generate question: {str(e)}")

def generate_followup_question(client):
    """Generate a follow-up question based on the last user response"""
    try:
        messages = st.session_state.get('conversation_history', [])
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        if not user_messages:
            st.warning("⚠️ No user responses yet to create a follow-up question.")
            return
        
        last_user_response = user_messages[-1]['content']
        
        with st.spinner("🔄 Generating follow-up question..."):
            prompt = f"""The candidate just responded: "{last_user_response}"

Generate a thoughtful follow-up question that:
- Digs deeper into their specific approach or reasoning
- Explores alternatives they might have considered
- Tests their understanding of trade-offs and decision-making
- Shows genuine curiosity about their experience
- Avoids generic follow-ups

Return only the follow-up question, make it specific and insightful."""
            
            followup = get_groq_response(client, prompt, [])
            add_message('assistant', f"🔄 **Follow-up Question:**\n\n{followup}")
        
        st.session_state.question_count = st.session_state.get('question_count', 0) + 1
        st.success("✅ Follow-up question generated!")
        
    except Exception as e:
        st.error(f"Failed to generate follow-up: {str(e)}")

def skip_to_next_stage(client):
    """Skip to the next interview stage"""
    try:
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
            'info_collection': "📝 **Skipped to Information Collection**\n\nLet's gather some details about your background.",
            'technical_assessment': "💻 **Skipped to Technical Assessment**\n\nNow let's dive into some technical questions based on your skills.",
            'behavioral_assessment': "🤝 **Skipped to Behavioral Assessment**\n\nLet's explore your soft skills and work approach using STAR methodology.",
            'wrap_up': generate_interview_completion()
        }
        
        message = transition_messages.get(next_stage, "Moving to the next stage...")
        add_message('assistant', message)
        
        st.success(f"⏭️ Skipped to: {next_stage.replace('_', ' ').title()}")
        
    except Exception as e:
        st.error(f"Failed to skip stage: {str(e)}")

def generate_interview_summary(client):
    """Generate AI-powered interview summary"""
    try:
        messages = st.session_state.get('conversation_history', [])
        candidate_info = st.session_state.get('candidate_info', {})
        
        if len(messages) < 4:
            st.warning("⚠️ Need more conversation data to generate a meaningful summary.")
            return
        
        with st.spinner("📊 AI is analyzing the interview..."):
            # Create conversation summary for analysis
            conversation_text = ""
            for msg in messages[-10:]:  # Last 10 messages
                role = "Interviewer" if msg.get('role') == 'assistant' else "Candidate"
                conversation_text += f"{role}: {msg.get('content', '')}\n\n"
            
            prompt = f"""Analyze this interview conversation and provide a comprehensive summary:

**Candidate Information:**
{candidate_info}

**Recent Conversation:**
{conversation_text}

Provide a structured summary including:
1. **Candidate Profile** - Key background details
2. **Technical Strengths** - Demonstrated skills and knowledge
3. **Communication Style** - How they articulate responses
4. **Areas for Follow-up** - Questions to explore further
5. **Overall Assessment** - Initial impression and recommendations

Keep it professional, balanced, and actionable."""
            
            summary = get_groq_response(client, prompt, [])
            add_message('assistant', f"📊 **AI Interview Summary:**\n\n{summary}")
        
        st.success("📋 Interview summary generated!")
        
    except Exception as e:
        st.error(f"Failed to generate summary: {str(e)}")

def repeat_last_question():
    """Repeat the last question asked by the AI"""
    try:
        messages = st.session_state.get('conversation_history', [])
        ai_messages = [m for m in messages if m.get('role') == 'assistant']
        
        if not ai_messages:
            st.warning("⚠️ No previous questions to repeat.")
            return
        
        last_ai_message = ai_messages[-1]['content']
        add_message('assistant', f"🔄 **Repeating Last Question:**\n\n{last_ai_message}")
        
        st.info("🔄 Last question repeated for clarity.")
        
    except Exception as e:
        st.error(f"Failed to repeat question: {str(e)}")

def handle_chat_input(client):
    """Handle user input with proper flow management"""
    user_input = st.chat_input("Type your response here...")
    
    if user_input and user_input.strip():
        # Add user message
        add_message('user', user_input)
        
        # Extract information based on current stage
        extract_candidate_info(user_input)
        
        # Generate appropriate AI response
        with st.spinner("🤖 AI is thinking..."):
            ai_response = generate_contextual_response(client, user_input)
            add_message('assistant', ai_response)
            
            # Update counters and check for stage advancement
            st.session_state.question_count = st.session_state.get('question_count', 0) + 1
            check_stage_advancement()
            
            st.rerun()

def extract_candidate_info(user_input):
    """Simplified but robust information extraction"""
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    
    candidate_info = st.session_state.candidate_info
    user_clean = user_input.strip()
    user_lower = user_clean.lower()
    
    # Determine what we're currently asking for based on what's missing
    if 'name' not in candidate_info:
        candidate_info['name'] = user_clean.title()
    
    elif 'email' not in candidate_info:
        if '@' in user_clean:
            candidate_info['email'] = user_clean
    
    elif 'experience' not in candidate_info:
        # Handle all possible experience formats
        if user_clean.isdigit():
            candidate_info['experience'] = f"{user_clean} years"
        elif 'year' in user_lower or 'exp' in user_lower:
            candidate_info['experience'] = user_clean
        elif 'fresh' in user_lower or user_clean == '0':
            candidate_info['experience'] = "Fresher"
        else:
            candidate_info['experience'] = f"{user_clean} years"
    
    elif 'position' not in candidate_info:
        candidate_info['position'] = user_clean.title()
    
    elif 'tech_stack' not in candidate_info:
        candidate_info['tech_stack'] = user_clean

def generate_contextual_response(client, user_input):
    """Generate contextual AI response with proper stage management"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    # Check what information we still need
    required_info = ['name', 'email', 'experience', 'position', 'tech_stack']
    missing_info = [field for field in required_info if field not in candidate_info or not candidate_info[field]]
    
    if stage == 'greeting' or stage == 'info_collection':
        if missing_info:
            next_field = missing_info[0]
            
            field_questions = {
                'name': f"Nice to meet you, **{candidate_info.get('name', 'there')}**! Could you please share your **email address**?",
                'email': f"Perfect! Now, how many **years of professional experience** do you have, {candidate_info.get('name', '')}?",
                'experience': f"Great! **{candidate_info.get('experience', '')}** of experience is excellent. What **type of position** are you interested in or currently working in?",
                'position': f"Perfect! **{candidate_info.get('position', '')}** is a great field. What are your main **technical skills and technologies**? (e.g., Python, React, AWS, etc.)",
                'tech_stack': "Thank you for that information!"
            }
            
            if 'name' in candidate_info and next_field == 'email':
                return field_questions['name']
            elif 'email' in candidate_info and next_field == 'experience':
                return field_questions['email']
            elif 'experience' in candidate_info and next_field == 'position':
                return field_questions['experience']
            elif 'position' in candidate_info and next_field == 'tech_stack':
                return field_questions['position']
            else:
                return field_questions.get(next_field, "Could you tell me more about that?")
        else:
            # All basic info collected, transition to technical
            tech_stack = candidate_info.get('tech_stack', 'programming')
            st.session_state.current_stage = 'technical_assessment'
            
            return f"""Perfect! I now have all your information:

**📋 Profile Summary:**
- **Name:** {candidate_info.get('name', 'Not provided')}
- **Email:** {candidate_info.get('email', 'Not provided')}
- **Experience:** {candidate_info.get('experience', 'Not specified')}
- **Position:** {candidate_info.get('position', 'Not specified')}
- **Tech Stack:** {candidate_info.get('tech_stack', 'Not specified')}

Now let's move to the **technical assessment** phase! 💻

**First Technical Question:**
Can you describe a challenging project you've worked on recently using {tech_stack}? Walk me through your approach, the problems you faced, and how you solved them."""
    
    elif stage == 'technical_assessment':
        return "Great response! Tell me more about how you would optimize performance in your applications."
    
    elif stage == 'behavioral_assessment':
        return "Excellent! Can you tell me about a time when you had to work with a difficult team member?"
    
    else:
        return "Thank you for your response. Let's continue with the interview."

def generate_interview_completion():
    """Generate completion message"""
    name = st.session_state.candidate_info.get('name', 'there')
    
    return f"""🎉 **Interview Complete!**

Thank you for your time, **{name}**! You've successfully completed our comprehensive AI-powered interview.

**Interview Summary:**
- ✅ **Personal Information:** Collected
- ✅ **Technical Assessment:** Completed  
- ✅ **Behavioral Evaluation:** Completed
- ✅ **Total Duration:** {calculate_duration()}
- ✅ **Questions Answered:** {st.session_state.get('question_count', 0)}

**Next Steps:**
1. Our team will review your detailed responses
2. You'll receive feedback within 2-3 business days
3. We'll be in touch regarding potential next steps

Thank you for choosing TalentScout AI! 🚀"""

def check_stage_advancement():
    """Check and advance interview stages automatically"""
    candidate_info = st.session_state.get('candidate_info', {})
    required_info = ['name', 'email', 'experience', 'position', 'tech_stack']
    
    # Auto-advance from greeting to info_collection
    if st.session_state.current_stage == 'greeting' and len(st.session_state.conversation_history) >= 4:
        st.session_state.current_stage = 'info_collection'
    
    # Auto-advance from info_collection to technical when all info collected
    elif st.session_state.current_stage == 'info_collection':
        if all(field in candidate_info for field in required_info):
            st.session_state.current_stage = 'technical_assessment'

def get_groq_response(client, prompt, conversation_history):
    """Get response from GROQ API"""
    try:
        messages = [
            {
                "role": "system",
                "content": """You are a professional AI interviewer. Be conversational and engaging. 
                Ask follow-up questions and show interest in the candidate's responses. Keep responses concise but thorough."""
            }
        ]
        
        for msg in conversation_history[-6:]:
            if msg.get('role') and msg.get('content'):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, I'm experiencing technical difficulties: {str(e)}"

def add_message(role, content):
    """Add message to conversation history"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    st.session_state.conversation_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now()
    })

def calculate_duration():
    """Calculate interview duration"""
    if st.session_state.get('interview_start_time'):
        duration = datetime.now() - st.session_state.interview_start_time
        minutes = duration.seconds // 60
        return f"{minutes} minutes"
    return "0 minutes"
