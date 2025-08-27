"""
TalentScout AI - Enhanced Advanced Chat Interface
Complete implementation with smart tech-specific question generation
"""

import streamlit as st
from datetime import datetime
import re
import random

def render_chat_interface(client):
    """Enhanced chat interface with smart question generation"""
    
    st.header("💬 Interview Chat")
    
    # Display conversation history
    display_chat_messages()
    
    # Interview controls
    if not st.session_state.get('interview_started', False):
        render_start_button(client)
    else:
        # Show current stage info and enhanced controls
        render_stage_info_and_controls(client)
        # Handle user input
        handle_chat_input(client)

def display_chat_messages():
    """Display all chat messages with proper formatting"""
    messages = st.session_state.get('conversation_history', [])
    
    if not messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("""
            👋 **Welcome to TalentScout AI!**
            
            I'm your AI interviewer, powered by **Llama 3.3 70B**. I'll conduct a comprehensive interview by:
            
            🎯 **Smart Question Generation:**
            - **Single Tech** (e.g., "Python") → Deep Python-focused questions
            - **Multiple Tech** (e.g., "Python, GenAI, LLM") → Integration questions covering ALL technologies
            
            💻 **Adaptive Interview Flow:**
            - Auto-generates diverse questions
            - Handles skip requests intelligently  
            - Provides real-time analytics
            - Professional interview experience
            
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
    """Enhanced stage info with smart controls"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    # Stage information with tech focus
    tech_stack = candidate_info.get('tech_stack', '')
    tech_count = len([tech.strip() for tech in tech_stack.split(',') if tech.strip()]) if tech_stack else 0
    tech_mode = f"Single-Tech Focus: {tech_stack}" if tech_count == 1 else f"Multi-Tech Integration: {tech_count} technologies"
    
    stage_messages = {
        'greeting': "👋 **Current Stage:** Initial Greeting",
        'info_collection': f"📝 **Current Stage:** Information Collection (Collected: {len(candidate_info)} items)",
        'technical_assessment': f"💻 **Current Stage:** Technical Assessment | {tech_mode}",
        'behavioral_assessment': f"🧠 **Current Stage:** Behavioral Assessment", 
        'wrap_up': "✅ **Current Stage:** Interview Complete"
    }
    
    st.info(stage_messages.get(stage, "Interview in progress..."))
    
    # Enhanced Controls Section
    if stage in ['technical_assessment', 'behavioral_assessment']:
        st.markdown("---")
        
        # Auto-generation toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("🎛️ Smart Interview Controls")
        with col2:
            auto_gen = st.toggle("🤖 Auto-Gen", value=st.session_state.get('auto_generate_questions', True))
            st.session_state.auto_generate_questions = auto_gen
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Smart Question", use_container_width=True, type="primary"):
                generate_smart_question(client)
                st.rerun()
        
        with col2:
            if st.button("🔄 Follow-up", use_container_width=True, type="secondary"):
                generate_smart_followup(client)
                st.rerun()
        
        with col3:
            if st.button("⏭️ Skip Topic", use_container_width=True, type="secondary"):
                skip_current_topic(client)
                st.rerun()
        
        # Additional controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Summary", use_container_width=True):
                generate_interview_summary(client)
                st.rerun()
        
        with col2:
            if st.button("🔄 Repeat Question", use_container_width=True):
                repeat_last_question()
                st.rerun()
        
        with col3:
            if st.button("⏭️ Next Stage", use_container_width=True):
                advance_to_next_stage(client)
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
    st.session_state.auto_generate_questions = True
    st.session_state.current_tech_focus = 0
    st.session_state.skip_requests = 0
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Generate initial greeting
    greeting = """Hello! I'm your AI interviewer from TalentScout. I'll conduct a comprehensive technical interview with **intelligent question generation**.

✨ **Smart Features:**
- **Tech-Specific Questions:** Single tech = deep dive, Multiple tech = integration
- **Auto-Generation:** Questions appear automatically based on your responses
- **Skip-Friendly:** Say "skip" or "next" to move forward anytime

Let's start with the basics. **What's your full name?**"""
    
    add_message('assistant', greeting)
    st.session_state.question_count += 1

def detect_skip_request(user_input):
    """Detect if user wants to skip current question/topic"""
    skip_indicators = [
        'skip', 'next', 'pass', 'dont want', "don't want", 'nothing', 
        'no idea', 'dont know', "don't know", 'move on', 'next question',
        'i have no idea', 'no experience', 'not sure', 'unsure'
    ]
    
    user_lower = user_input.lower().strip()
    
    # Check for explicit skip words
    explicit_skip = any(indicator in user_lower for indicator in skip_indicators)
    
    # Check for very short responses (likely avoidance)
    too_short = len(user_input.strip()) <= 4
    
    # Check for single word responses that indicate skipping
    single_word_skip = user_input.strip().lower() in ['okay', 'ok', 'yes', 'no', 'idk', 'nope']
    
    return explicit_skip or (too_short and single_word_skip)

def handle_chat_input(client):
    """Enhanced chat input with skip detection and auto-generation"""
    user_input = st.chat_input("Type your response... (say 'skip' to move to next question)")
    
    if user_input and user_input.strip():
        # Add user message
        add_message('user', user_input)
        
        # Check for skip request
        if detect_skip_request(user_input):
            st.session_state.skip_requests = st.session_state.get('skip_requests', 0) + 1
            handle_skip_request(client)
        else:
            # Reset skip counter on normal response
            st.session_state.skip_requests = 0
            # Extract information based on current stage
            extract_candidate_info(user_input)
            
            # Generate appropriate AI response
            with st.spinner("🤖 AI is analyzing your response..."):
                ai_response = generate_contextual_response(client, user_input)
                add_message('assistant', ai_response)
                
                # Auto-generate follow-up if enabled and in assessment stages
                if (st.session_state.get('auto_generate_questions', True) and 
                    st.session_state.get('current_stage') in ['technical_assessment', 'behavioral_assessment']):
                    auto_generate_next_question(client)
                
                # Update counters and check for stage advancement
                st.session_state.question_count = st.session_state.get('question_count', 0) + 1
                check_stage_advancement()
        
        st.rerun()

def handle_skip_request(client):
    """Handle user skip requests intelligently"""
    stage = st.session_state.get('current_stage', 'greeting')
    skip_count = st.session_state.get('skip_requests', 0)
    
    if stage == 'behavioral_assessment' and skip_count >= 3:
        # Multiple skips in behavioral - move to wrap up
        st.session_state.current_stage = 'wrap_up'
        completion_msg = generate_interview_completion()
        add_message('assistant', completion_msg)
    elif stage in ['technical_assessment', 'behavioral_assessment']:
        # Generate alternative question in same stage
        add_message('assistant', "No problem! Let me try a different approach.")
        generate_alternative_question(client)
    else:
        # Default skip handling
        add_message('assistant', "Understood! Let me ask something different.")
        if st.session_state.get('auto_generate_questions', True):
            auto_generate_next_question(client)

def generate_alternative_question(client):
    """Generate alternative question when user skips"""
    stage = st.session_state.get('current_stage', 'technical_assessment')
    candidate_info = st.session_state.get('candidate_info', {})
    
    if stage == 'technical_assessment':
        alt_question = get_alternative_technical_question(candidate_info)
        add_message('assistant', f"**Alternative Technical Question:**\n\n{alt_question}")
    elif stage == 'behavioral_assessment':
        alt_question = get_alternative_behavioral_question()
        add_message('assistant', f"**Alternative Behavioral Question:**\n\n{alt_question}")

def get_alternative_technical_question(candidate_info):
    """Get alternative technical questions based on tech stack"""
    tech_stack = candidate_info.get('tech_stack', 'programming')
    technologies = [tech.strip() for tech in tech_stack.split(',') if tech.strip()]
    
    if len(technologies) == 1:
        # Single tech alternatives
        single_tech = technologies[0]
        alt_questions = [
            f"**Basic Concepts:** What are the key features of {single_tech} that make it suitable for your projects?",
            f"**Problem-Solving:** How would you debug a performance issue in a {single_tech} application?",
            f"**Best Practices:** What coding standards do you follow when writing {single_tech} code?"
        ]
    else:
        # Multi-tech alternatives
        alt_questions = [
            f"**Technology Choice:** Why would you choose {technologies[0]} over other alternatives for a new project?",
            f"**Integration:** How do these technologies ({', '.join(technologies)}) complement each other in your work?",
            f"**Learning:** Which of these technologies ({', '.join(technologies)}) did you find most challenging to learn and why?"
        ]
    
    return random.choice(alt_questions)

def get_alternative_behavioral_question():
    """Get simple alternative behavioral questions"""
    alt_questions = [
        "**Learning:** Tell me about a new skill you learned recently. How did you approach it?",
        "**Challenges:** Describe a work challenge you faced. How did you handle it?",
        "**Teamwork:** How do you prefer to work - independently or in a team? Why?",
        "**Goals:** What are your career goals for the next 2-3 years?",
        "**Motivation:** What motivates you most in your work?"
    ]
    
    return random.choice(alt_questions)

def auto_generate_next_question(client):
    """Auto-generate next question based on stage and tech stack"""
    if not st.session_state.get('auto_generate_questions', True):
        return
    
    stage = st.session_state.get('current_stage', 'greeting')
    
    if stage == 'technical_assessment':
        generate_smart_question(client, auto=True)
    elif stage == 'behavioral_assessment':
        generate_smart_behavioral_question(client, auto=True)

def generate_smart_question(client, auto=False):
    """Generate questions based on single vs multiple technologies"""
    try:
        candidate_info = st.session_state.get('candidate_info', {})
        tech_stack = candidate_info.get('tech_stack', 'programming')
        experience = candidate_info.get('experience', '2-3 years')
        technologies = [tech.strip() for tech in tech_stack.split(',') if tech.strip()]
        tech_count = len(technologies)
        
        with st.spinner("🧠 Generating smart question..."):
            
            if tech_count == 1:
                # SINGLE TECHNOLOGY - Deep dive questions
                single_tech = technologies[0]
                
                prompt = f"""Create a focused technical question for {single_tech} with {experience} experience.

Requirements:
- Focus EXCLUSIVELY on {single_tech}
- Test practical knowledge and real-world application
- Include scenario-based problem solving
- Appropriate difficulty for {experience} level
- Avoid generic questions

Format: Present a specific {single_tech} challenge or technical scenario."""
                
                prefix = f"🐍 **{single_tech}-Focused Question:**" if auto else f"🎯 **Deep {single_tech} Question:**"
                
            else:
                # MULTIPLE TECHNOLOGIES - Integration questions
                all_techs = ', '.join(technologies)
                
                prompt = f"""Create a technical question that integrates {all_techs} for {experience} experience.

Requirements:
- Combine ALL technologies: {all_techs}
- Focus on integration and how they work together
- Real-world system design scenario
- Test understanding of technology interactions
- Include architecture considerations

Format: Present a system integration challenge using all {tech_count} technologies."""
                
                prefix = f"🔗 **Multi-Tech Integration:**" if auto else f"🎯 **{tech_count}-Technology Question:**"
            
            # Generate the question
            ai_question = get_groq_response(client, prompt, [])
            add_message('assistant', f"{prefix}\n\n{ai_question}")
        
        if not auto:
            tech_type = "single-technology" if tech_count == 1 else "multi-technology integration"
            st.success(f"✨ {tech_type.title()} question generated!")
        
    except Exception as e:
        st.error(f"Failed to generate question: {str(e)}")

def generate_smart_behavioral_question(client, auto=False):
    """Generate smart behavioral questions"""
    try:
        behavioral_topics = [
            "Problem-Solving and Critical Thinking",
            "Team Collaboration and Communication", 
            "Learning and Professional Development",
            "Leadership and Initiative",
            "Adaptability and Change Management",
            "Time Management and Prioritization"
        ]
        
        topic = random.choice(behavioral_topics)
        
        with st.spinner("🧠 Generating behavioral question..."):
            prompt = f"""Create a behavioral interview question about "{topic}":

Requirements:
- Use STAR method (Situation, Task, Action, Result)
- Make it specific and scenario-based
- Relate to professional work environment
- Encourage detailed examples
- Test both skill and self-awareness

Format: Ask for a specific example using STAR format."""
            
            behavioral_question = get_groq_response(client, prompt, [])
            
            prefix = "🧠 **Auto-Generated Behavioral:**" if auto else "🎯 **Smart Behavioral Question:**"
            add_message('assistant', f"{prefix}\n\n{behavioral_question}")
        
        if not auto:
            st.success("✨ Behavioral question generated!")
        
    except Exception as e:
        st.error(f"Failed to generate behavioral question: {str(e)}")

def generate_smart_followup(client):
    """Generate intelligent follow-up questions"""
    try:
        messages = st.session_state.get('conversation_history', [])
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        if not user_messages:
            st.warning("⚠️ No responses yet to create follow-up questions.")
            return
        
        last_response = user_messages[-1]['content']
        
        with st.spinner("🔄 Generating smart follow-up..."):
            prompt = f"""The candidate responded: "{last_response}"

Generate a thoughtful follow-up question that:
- Digs deeper into their specific approach
- Explores their decision-making process  
- Tests understanding of alternatives and trade-offs
- Shows genuine curiosity about their experience
- Avoids generic follow-ups

Make it specific and insightful."""
            
            followup = get_groq_response(client, prompt, [])
            add_message('assistant', f"🔄 **Smart Follow-up:**\n\n{followup}")
        
        st.success("✅ Smart follow-up generated!")
        
    except Exception as e:
        st.error(f"Failed to generate follow-up: {str(e)}")

def skip_current_topic(client):
    """Skip current topic and move to different area"""
    try:
        stage = st.session_state.get('current_stage', 'technical_assessment')
        
        if stage == 'technical_assessment':
            add_message('assistant', "Let's explore a different technical area.")
            generate_smart_question(client)
        elif stage == 'behavioral_assessment':
            add_message('assistant', "No problem! Let's focus on a different aspect of your experience.")
            generate_smart_behavioral_question(client)
        
        st.success("⏭️ Moved to different topic!")
        
    except Exception as e:
        st.error(f"Failed to skip topic: {str(e)}")

def generate_interview_summary(client):
    """Generate AI-powered interview summary"""
    try:
        messages = st.session_state.get('conversation_history', [])
        candidate_info = st.session_state.get('candidate_info', {})
        
        if len(messages) < 6:
            st.warning("⚠️ Need more conversation data for meaningful summary.")
            return
        
        with st.spinner("📊 AI is analyzing the interview..."):
            conversation_text = ""
            for msg in messages[-12:]:
                role = "Interviewer" if msg.get('role') == 'assistant' else "Candidate"
                conversation_text += f"{role}: {msg.get('content', '')[:200]}...\n\n"
            
            prompt = f"""Analyze this interview and provide a professional summary:

**Candidate:** {candidate_info}

**Recent Conversation:**
{conversation_text}

Provide:
1. **Technical Strengths** - Key skills demonstrated
2. **Communication Style** - How they articulate responses  
3. **Problem-Solving Approach** - Their methodology
4. **Areas for Follow-up** - Topics to explore further
5. **Overall Assessment** - Initial impression

Keep it professional and actionable."""
            
            summary = get_groq_response(client, prompt, [])
            add_message('assistant', f"📊 **AI Interview Analysis:**\n\n{summary}")
        
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
        add_message('assistant', f"🔄 **Repeating for Clarity:**\n\n{last_ai_message}")
        
        st.info("🔄 Last question repeated.")
        
    except Exception as e:
        st.error(f"Failed to repeat question: {str(e)}")

def advance_to_next_stage(client):
    """Advance to the next interview stage"""
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
            'info_collection': "📝 **Information Collection Phase**\n\nLet's gather details about your background.",
            'technical_assessment': "💻 **Technical Assessment Phase**\n\nTime for technical questions based on your skills.",
            'behavioral_assessment': "🧠 **Behavioral Assessment Phase**\n\nLet's explore your soft skills and work approach.",
            'wrap_up': generate_interview_completion()
        }
        
        message = transition_messages.get(next_stage, "Moving to next stage...")
        add_message('assistant', message)
        
        st.success(f"⏭️ Advanced to: {next_stage.replace('_', ' ').title()}")
        
    except Exception as e:
        st.error(f"Failed to advance stage: {str(e)}")

def extract_candidate_info(user_input):
    """Robust information extraction with improved logic"""
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    
    candidate_info = st.session_state.candidate_info
    user_clean = user_input.strip()
    user_lower = user_clean.lower()
    
    # Determine current question based on missing info
    required_fields = ['name', 'email', 'experience', 'position', 'tech_stack']
    
    for field in required_fields:
        if field not in candidate_info:
            if field == 'name':
                candidate_info['name'] = user_clean.title()
                break
            elif field == 'email':
                if '@' in user_clean:
                    candidate_info['email'] = user_clean
                break
            elif field == 'experience':
                # Enhanced experience extraction
                if user_clean.isdigit():
                    candidate_info['experience'] = f"{user_clean} years"
                elif any(word in user_lower for word in ['year', 'exp', 'yr']):
                    candidate_info['experience'] = user_clean
                elif any(word in user_lower for word in ['fresh', 'new', 'graduate']):
                    candidate_info['experience'] = "Fresher"
                else:
                    # Default: treat as years
                    candidate_info['experience'] = f"{user_clean} years"
                break
            elif field == 'position':
                candidate_info['position'] = user_clean.title()
                break
            elif field == 'tech_stack':
                candidate_info['tech_stack'] = user_clean
                break

def generate_contextual_response(client, user_input):
    """Generate contextual AI response with proper flow"""
    stage = st.session_state.get('current_stage', 'greeting')
    candidate_info = st.session_state.get('candidate_info', {})
    
    required_info = ['name', 'email', 'experience', 'position', 'tech_stack']
    missing_info = [field for field in required_info if field not in candidate_info]
    
    if stage in ['greeting', 'info_collection']:
        if missing_info:
            next_field = missing_info[0]
            
            field_questions = {
                'name': f"Nice to meet you, **{candidate_info.get('name', 'there')}**! Could you please share your **email address**?",
                'email': f"Perfect! How many **years of professional experience** do you have, {candidate_info.get('name', '')}?",
                'experience': f"Great! **{candidate_info.get('experience', '')}** is excellent. What **type of position** are you interested in?",
                'position': f"Perfect! What are your main **technical skills and technologies**?\n\n*Please list all technologies you work with (e.g., Python, GenAI, LLM, React, etc.)*",
                'tech_stack': "Thank you for that comprehensive information!"
            }
            
            # Return appropriate question based on what was just collected
            last_collected = list(candidate_info.keys())[-1] if candidate_info else None
            if last_collected and last_collected != next_field:
                return field_questions.get(last_collected, field_questions.get(next_field, "Tell me more."))
            else:
                return field_questions.get(next_field, "Could you tell me more?")
        else:
            # All info collected - transition to technical
            tech_stack = candidate_info.get('tech_stack', 'programming')
            technologies = [tech.strip() for tech in tech_stack.split(',') if tech.strip()]
            tech_count = len(technologies)
            
            st.session_state.current_stage = 'technical_assessment'
            
            if tech_count == 1:
                return f"""Perfect! I see you specialize in **{technologies[0]}**.

**📋 Complete Profile:**
- **Name:** {candidate_info.get('name', 'Not provided')}
- **Experience:** {candidate_info.get('experience', 'Not specified')}
- **Position:** {candidate_info.get('position', 'Not specified')}
- **Technology:** {candidate_info.get('tech_stack', 'Not specified')}

🎯 **Assessment Strategy:** Since you work with {technologies[0]}, I'll generate **focused questions specifically about {technologies[0]}** - covering advanced concepts, best practices, and real-world applications.

**🚀 Starting {technologies[0]}-focused technical assessment...**

*Auto-generating your first {technologies[0]} question...*"""
            
            else:
                return f"""Excellent! I see you work with **{tech_count} technologies:** {', '.join(technologies)}.

**📋 Complete Profile:**
- **Name:** {candidate_info.get('name', 'Not provided')}
- **Experience:** {candidate_info.get('experience', 'Not specified')}
- **Position:** {candidate_info.get('position', 'Not specified')}
- **Technologies:** {candidate_info.get('tech_stack', 'Not specified')}

🎯 **Assessment Strategy:** Since you work with multiple technologies, I'll generate **integration questions that combine {', '.join(technologies)}** - testing how you use them together in real-world scenarios.

**🚀 Starting multi-technology integration assessment...**

*Auto-generating your first integration question covering all {tech_count} technologies...*"""
    
    elif stage == 'technical_assessment':
        return "Excellent technical insight! Your approach shows strong problem-solving skills."
    
    elif stage == 'behavioral_assessment':
        return "Great example! That demonstrates strong professional competencies."
    
    else:
        return "Thank you for that detailed response. Your experience is valuable."

def check_stage_advancement():
    """Check and advance interview stages automatically"""
    candidate_info = st.session_state.get('candidate_info', {})
    required_info = ['name', 'email', 'experience', 'position', 'tech_stack']
    
    # Auto-advance based on conversation length and info completion
    if st.session_state.current_stage == 'greeting' and len(st.session_state.conversation_history) >= 4:
        st.session_state.current_stage = 'info_collection'
    
    elif st.session_state.current_stage == 'info_collection':
        if all(field in candidate_info for field in required_info):
            st.session_state.current_stage = 'technical_assessment'

def get_groq_response(client, prompt, conversation_history):
    """Get response from GROQ API with enhanced prompting"""
    try:
        messages = [
            {
                "role": "system",
                "content": """You are a professional technical interviewer. Create engaging, specific questions that test both technical knowledge and practical application. 

Guidelines:
- Be conversational and show genuine interest
- Ask one focused question at a time
- Make questions scenario-based and practical
- Adapt difficulty to candidate's experience level
- Avoid generic or textbook questions"""
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
            temperature=0.8,  # Higher creativity for diverse questions
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, I'm experiencing technical difficulties: {str(e)}"

def generate_interview_completion():
    """Generate comprehensive completion message"""
    name = st.session_state.candidate_info.get('name', 'there')
    tech_stack = st.session_state.candidate_info.get('tech_stack', 'your technologies')
    
    return f"""🎉 **Interview Successfully Completed!**

Thank you for your time, **{name}**! You've completed our comprehensive AI-powered technical interview.

**📊 Interview Summary:**
- ✅ **Technology Assessment:** {tech_stack}
- ✅ **Questions Generated:** {st.session_state.get('question_count', 0)}
- ✅ **Duration:** {calculate_duration()}
- ✅ **Stages Completed:** All phases ✅

**🎯 Key Highlights:**
- Demonstrated technical expertise across your technology stack
- Showed adaptability with AI-generated personalized questions
- Maintained professional engagement throughout the process

**📋 Assessment Coverage:**
- **Technical Depth:** Advanced concepts and real-world applications
- **Problem-Solving:** Scenario-based challenges
- **Communication:** Clear articulation of technical concepts
- **Professional Skills:** Behavioral competencies

**🚀 Next Steps:**
1. **Comprehensive Review:** Technical team analyzes your responses
2. **Feedback Timeline:** You'll hear back within 24-48 hours
3. **Potential Follow-up:** Technical deep-dive or team interviews
4. **Decision Process:** Final decision within 3-5 business days

**💡 Interview Innovations Used:**
- AI-powered question generation
- Technology-specific vs integration testing
- Real-time conversation adaptation
- Professional assessment methodology

Thank you for choosing TalentScout AI - where intelligence meets talent! 🌟

*Your interview data has been securely recorded for review.*"""

def add_message(role, content):
    """Add message to conversation history with metadata"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    st.session_state.conversation_history.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now(),
        'stage': st.session_state.get('current_stage', 'greeting')
    })

def calculate_duration():
    """Calculate and format interview duration"""
    if st.session_state.get('interview_start_time'):
        duration = datetime.now() - st.session_state.interview_start_time
        minutes = duration.seconds // 60
        seconds = duration.seconds % 60
        
        if minutes > 0:
            return f"{minutes} minutes {seconds} seconds"
        else:
            return f"{seconds} seconds"
    return "0 minutes"
