"""
Enhanced Advanced Chat Interface with Fixed Conversation Flow
"""

import streamlit as st
from datetime import datetime
import re

def render_chat_interface(client):
    """Enhanced chat interface with proper conversation flow"""
    
    st.header("💬 Interview Chat")
    
    # Display conversation history
    display_chat_messages()
    
    # Interview controls
    if not st.session_state.get('interview_started', False):
        render_start_button(client)
    else:
        # Show current stage info
        stage_info()
        # Handle user input
        handle_chat_input(client)

def display_chat_messages():
    """Display all chat messages properly"""
    messages = st.session_state.get('conversation_history', [])
    
    if not messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
            👋 **Welcome to TalentScout AI!**
            
            I'm your AI interviewer, powered by Llama 3.3 70B. I'll conduct a structured technical interview by:
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

def stage_info():
    """Show current interview stage"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    stage_messages = {
        'greeting': "👋 **Current Stage:** Initial Greeting",
        'info_collection': f"📝 **Current Stage:** Information Collection (Collected: {len(candidate_info)} items)",
        'technical_assessment': "💻 **Current Stage:** Technical Assessment",
        'behavioral_assessment': "🧠 **Current Stage:** Behavioral Assessment", 
        'wrap_up': "✅ **Current Stage:** Interview Complete"
    }
    
    st.info(stage_messages.get(stage, "Interview in progress..."))

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
    """Enhanced information extraction with better logic"""
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    
    candidate_info = st.session_state.candidate_info
    user_lower = user_input.lower().strip()
    
    # Extract name (improved logic)
    if 'name' not in candidate_info:
        # Look for name patterns
        name_patterns = [
            r'my name is (.+)', r'i am (.+)', r"i'm (.+)",
            r'name is (.+)', r'call me (.+)'
        ]
        
        name_found = False
        for pattern in name_patterns:
            match = re.search(pattern, user_lower)
            if match:
                name = match.group(1).strip()
                # Clean up common words
                name = re.sub(r'\b(a|an|the|and|or|but)\b', '', name).strip()
                if name and len(name) > 1:
                    candidate_info['name'] = name.title()
                    name_found = True
                    break
        
        # If no pattern match, check if input looks like just a name
        if not name_found and len(user_input.split()) <= 3 and not any(char in user_input for char in '@.'):
            # Likely just a name
            candidate_info['name'] = user_input.strip().title()
    
    # Extract email
    if 'email' not in candidate_info:
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        if email_match:
            candidate_info['email'] = email_match.group()
    
    # **FIXED: Experience extraction with multiple approaches**
    if 'experience' not in candidate_info:
        # Approach 1: Check if it's just a number (like "2", "5", "10")
        if user_input.strip().isdigit():
            years = int(user_input.strip())
            if 0 <= years <= 50:  # Reasonable range for years of experience
                candidate_info['experience'] = f"{years} years"
        
        # Approach 2: Look for explicit year patterns
        elif not candidate_info.get('experience'):
            exp_patterns = [
                r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
                r'(?:experience|exp)\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)',
                r'(\d+)\+?\s*(?:years?|yrs?)',
                r'over\s*(\d+)\s*(?:years?|yrs?)',
                r'about\s*(\d+)\s*(?:years?|yrs?)',
                r'around\s*(\d+)\s*(?:years?|yrs?)',
                r'(\d+)\s*year',  # Simple "2 year" or "5 years"
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, user_lower)
                if match:
                    years = match.group(1)
                    candidate_info['experience'] = f"{years} years"
                    break
        
        # Approach 3: Check for experience level words
        if not candidate_info.get('experience'):
            if any(word in user_lower for word in ['fresher', 'fresh', 'new graduate', 'entry', 'no experience', '0']):
                candidate_info['experience'] = "Fresher"
            elif any(word in user_lower for word in ['senior', 'lead', 'principal', 'experienced']):
                candidate_info['experience'] = "Senior level"
            elif 'junior' in user_lower:
                candidate_info['experience'] = "Junior level"
    
    # Extract position/role
    if 'position' not in candidate_info:
        tech_roles = [
            'software engineer', 'software developer', 'web developer', 'full stack',
            'frontend developer', 'backend developer', 'data scientist', 'data analyst',
            'machine learning engineer', 'ai engineer', 'devops', 'qa engineer',
            'python developer', 'java developer', 'react developer'
        ]
        
        for role in tech_roles:
            if role in user_lower:
                candidate_info['position'] = role.title()
                break
        
        # Simple role extraction if no specific match
        if 'position' not in candidate_info:
            if any(word in user_lower for word in ['engineer', 'developer', 'programmer', 'analyst']):
                candidate_info['position'] = user_input.strip().title()
    
    # Extract tech stack (improved)
    if 'tech_stack' not in candidate_info:
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'angular', 'vue',
            'django', 'flask', 'express', 'spring', 'sql', 'mongodb', 'postgresql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'html', 'css', 'php',
            'c++', 'c#', '.net', 'ruby', 'go', 'rust', 'swift', 'kotlin'
        ]
        
        mentioned_tech = []
        for tech in tech_keywords:
            if tech in user_lower or tech.replace('.', '') in user_lower:
                mentioned_tech.append(tech.title())
        
        if mentioned_tech:
            candidate_info['tech_stack'] = ', '.join(mentioned_tech)
        elif any(word in user_lower for word in ['programming', 'coding', 'development', 'tech', 'stack']):
            # If they mention general programming terms, use their input
            candidate_info['tech_stack'] = user_input.strip()

    # **Debug logging - remove this after testing**
    st.write(f"**Debug:** Extracted info so far: {candidate_info}")


def generate_contextual_response(client, user_input):
    """Generate contextual AI response with proper stage management"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    # Check what information we still need
    required_info = ['name', 'email', 'experience', 'position', 'tech_stack']
    missing_info = [field for field in required_info if field not in candidate_info]
    
    if stage == 'greeting' or stage == 'info_collection':
        if missing_info:
            # Still collecting information
            next_field = missing_info[0]
            
            field_questions = {
                'name': "Perfect! Now, could you please share your **email address**?",
                'email': "Great! How many **years of professional experience** do you have?",
                'experience': "Excellent! What **type of position** are you interested in or currently working in?",
                'position': "Perfect! What are your main **technical skills and technologies** you work with? (e.g., Python, React, AWS, etc.)",
                'tech_stack': "Thank you for sharing that information!"
            }
            
            # Get the appropriate question for the next missing field
            if next_field == 'name' and 'name' in candidate_info:
                # Name was just collected, ask for email
                return field_questions['name']
            elif next_field == 'email' and 'email' in candidate_info:
                return field_questions['email']
            elif next_field == 'experience' and 'experience' in candidate_info:
                return field_questions['experience']
            elif next_field == 'position' and 'position' in candidate_info:
                return field_questions['position']
            elif next_field == 'tech_stack' and 'tech_stack' in candidate_info:
                return field_questions['tech_stack']
            else:
                return field_questions.get(next_field, "Could you tell me more about that?")
        else:
            # All basic info collected, transition to technical
            tech_stack = candidate_info.get('tech_stack', 'programming')
            st.session_state.current_stage = 'technical_assessment'
            
            return f"""Perfect! I now have all your basic information:
- **Name:** {candidate_info.get('name', 'Not provided')}
- **Experience:** {candidate_info.get('experience', 'Not specified')}
- **Position:** {candidate_info.get('position', 'Not specified')}
- **Tech Stack:** {candidate_info.get('tech_stack', 'Not specified')}

Now let's move to the **technical assessment** phase! 💻

**First Technical Question:**

Can you describe a challenging project you've worked on recently using {tech_stack}? Walk me through your approach, the problems you faced, and how you solved them."""
    
    elif stage == 'technical_assessment':
        # Generate technical questions
        tech_stack = candidate_info.get('tech_stack', 'programming')
        question_num = st.session_state.get('question_count', 1) - len([field for field in required_info if field in candidate_info])
        
        technical_questions = [
            f"Great response! Now, how would you optimize the performance of a {tech_stack} application that's running slowly in production?",
            f"Interesting! Can you explain how you would design a scalable system architecture for a {tech_stack} application?",
            f"Excellent! Tell me about your experience with testing in {tech_stack}. What testing strategies do you use?",
            "Perfect! How do you handle error handling and debugging in your applications?",
            "Great insight! What's your approach to code review and maintaining code quality in a team environment?"
        ]
        
        if question_num < len(technical_questions):
            return technical_questions[question_num - 1]
        else:
            # Move to behavioral assessment
            st.session_state.current_stage = 'behavioral_assessment'
            return """🎉 **Technical Assessment Complete!**

You've demonstrated solid technical knowledge. Now let's explore your soft skills and work approach.

**First Behavioral Question:**

Tell me about a time when you had to work with a difficult team member or handle a challenging stakeholder situation. How did you manage it?"""
    
    elif stage == 'behavioral_assessment':
        behavioral_questions = [
            "Excellent example! Describe a situation where you had to learn a new technology quickly for a project. How did you approach it?",
            "Great! Tell me about a time when you had to meet a tight deadline. How did you ensure quality while working under pressure?",
            "Perfect! Give me an example of when you had to explain a complex technical concept to a non-technical team member.",
            "Thank you for sharing that! How do you handle feedback and criticism of your work?"
        ]
        
        question_num = len([m for m in st.session_state.conversation_history if m.get('role') == 'assistant' and 'behavioral' in m.get('content', '').lower()])
        
        if question_num < len(behavioral_questions):
            return behavioral_questions[question_num]
        else:
            # Move to wrap up
            st.session_state.current_stage = 'wrap_up'
            return generate_interview_completion()
    
    elif stage == 'wrap_up':
        return "Thank you for your additional thoughts! Is there anything else you'd like to add about your background or ask about the position?"
    
    # Default response
    return get_groq_response(client, f"Continue the interview conversation. User said: {user_input}", st.session_state.conversation_history)

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

**Key Strengths Observed:**
- Strong technical communication
- Good problem-solving approach
- Professional throughout the process

Thank you for choosing TalentScout AI! 🚀"""

def check_stage_advancement():
    """Check and advance interview stages"""
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
    """Get response from GROQ API as fallback"""
    try:
        messages = [
            {
                "role": "system",
                "content": """You are a professional AI interviewer. Be conversational and engaging. 
                Ask follow-up questions and show interest in the candidate's responses. Keep responses concise but thorough."""
            }
        ]
        
        # Add recent conversation context
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
        return f"I apologize, but I'm experiencing technical difficulties. Please try again. Error: {str(e)}"

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
