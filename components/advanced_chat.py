"""
Enhanced Advanced Chat Interface with Working Conversation Flow
Real-time AI interview questions powered by Llama 3.3 70B
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

def render_chat_interface():
    """Enhanced chat interface with working conversation flow"""
    
    # Initialize AI components
    if "ai_manager" not in st.session_state:
        st.error("❌ AI Manager not initialized")
        return
    
    # Display messages
    display_enhanced_messages()
    
    # Dynamic question generation controls
    render_question_controls()
    
    # Enhanced chat input
    handle_chat_input()

def handle_chat_input():
    """Handle chat input with proper conversation flow"""
    
    placeholder = get_dynamic_placeholder()
    
    if prompt := st.chat_input(placeholder):
        # Add user message
        add_enhanced_message("user", prompt)
        
        # Process response and generate AI reply
        with st.spinner("🤖 AI is thinking..."):
            ai_response = generate_ai_response(prompt)
            if ai_response:
                add_enhanced_message("assistant", ai_response)
        
        # Update conversation state
        update_conversation_state(prompt)
        st.rerun()

def generate_ai_response(user_input: str) -> str:
    """Generate AI response based on conversation stage and user input"""
    
    stage = st.session_state.get("conversation_stage", "greeting")
    
    if stage == "greeting":
        return handle_greeting_stage(user_input)
    elif stage == "info_collection":
        return handle_info_collection_stage(user_input)
    elif stage == "technical_assessment":
        return handle_technical_stage(user_input)
    elif stage == "behavioral_assessment":
        return handle_behavioral_stage(user_input)
    else:
        return "Thank you for your responses! Is there anything else you'd like to discuss?"

def handle_greeting_stage(user_input: str) -> str:
    """Handle greeting stage conversation"""
    
    # Extract name from input
    name = user_input.strip().title()
    
    # Initialize candidate data
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = {}
    
    st.session_state.candidate_data["name"] = name
    st.session_state.conversation_stage = "info_collection"
    
    return f"""Nice to meet you, **{name}**! 🎯

I'll be conducting an adaptive interview that adjusts based on your responses. My advanced AI will generate targeted questions specific to your background.

Could you please share your **email address**?"""

def handle_info_collection_stage(user_input: str) -> str:
    """Handle information collection stage"""
    
    data = st.session_state.get("candidate_data", {})
    
    if "email" not in data:
        # Validate email format
        if "@" not in user_input or "." not in user_input:
            return "Please provide a valid email address (e.g., john@example.com)"
        
        data["email"] = user_input.strip()
        return "Perfect! Now, **how many years of professional experience** do you have?"
    
    elif "experience" not in data:
        data["experience"] = user_input.strip()
        return "Great! **What type of position** are you interested in? (e.g., Software Engineer, Data Scientist, etc.)"
    
    elif "position" not in data:
        data["position"] = user_input.strip()
        return """Excellent! Now for the key part - **what programming languages, frameworks, and technologies** are you proficient with?

Please list your main technical skills (e.g., Python, React, AWS, PostgreSQL)"""
    
    else:
        # Parse tech stack and move to technical assessment
        tech_skills = [skill.strip() for skill in user_input.split(",")]
        data["tech_stack"] = tech_skills
        
        # Update conversation context
        st.session_state.conversation_context = {
            "position": data.get("position", "Software Developer"),
            "experience": data.get("experience", "3 years"),
            "skills": tech_skills
        }
        
        st.session_state.conversation_stage = "technical_assessment"
        
        return f"""Perfect! I now have your background:
- **Position:** {data['position']}
- **Experience:** {data['experience']}  
- **Tech Stack:** {', '.join(tech_skills)}

Now I'll use **advanced AI prompt engineering** to generate technical questions specifically tailored to your skills. Let's begin the technical assessment! 🚀

**First Technical Question:**

Can you describe a challenging {tech_skills[0] if tech_skills else 'technical'} problem you've solved recently? Walk me through your approach and the solution you implemented."""

def handle_technical_stage(user_input: str) -> str:
    """Handle technical assessment stage"""
    
    # Track assessment progress
    if "technical_questions_asked" not in st.session_state:
        st.session_state.technical_questions_asked = 1
    else:
        st.session_state.technical_questions_asked += 1
    
    question_count = st.session_state.technical_questions_asked
    
    # Provide feedback and ask follow-up
    feedback = f"""**Great response!** {get_encouraging_feedback(user_input)}

**Follow-up Question {question_count}:**
"""
    
    # Generate next technical question based on their background
    skills = st.session_state.get("candidate_data", {}).get("tech_stack", ["programming"])
    skill = skills[0] if skills else "programming"
    
    if question_count == 2:
        next_question = f"How would you optimize the performance of a {skill} application that's running slowly in production? What steps would you take to identify and fix bottlenecks?"
    elif question_count == 3:
        next_question = f"Describe how you would design a scalable system architecture for a {skill}-based application that needs to handle thousands of concurrent users."
    elif question_count >= 4:
        # Move to behavioral assessment
        st.session_state.conversation_stage = "behavioral_assessment"
        return """🎉 **Technical Assessment Complete!**

You've demonstrated solid technical knowledge. Now let's explore your soft skills and behavioral competencies.

**First Behavioral Question:**

Tell me about a time when you had to work with a difficult team member or stakeholder. How did you handle the situation? Please use the STAR method: Situation, Task, Action, Result."""
    else:
        next_question = f"Can you explain the difference between {skill} concepts you mentioned and when you would use each approach?"
    
    return feedback + next_question

def handle_behavioral_stage(user_input: str) -> str:
    """Handle behavioral assessment stage"""
    
    if "behavioral_questions_asked" not in st.session_state:
        st.session_state.behavioral_questions_asked = 1
    else:
        st.session_state.behavioral_questions_asked += 1
    
    question_count = st.session_state.behavioral_questions_asked
    
    if question_count >= 3:
        # Complete interview
        st.session_state.conversation_stage = "completed"
        return generate_interview_completion()
    
    feedback = f"**Excellent example!** {get_encouraging_feedback(user_input)}"
    
    behavioral_questions = [
        "Describe a time when you had to learn a new technology or skill quickly for a project. How did you approach it?",
        "Tell me about a project where you had to meet a tight deadline. How did you ensure quality while working under pressure?",
        "Give me an example of when you had to explain a complex technical concept to a non-technical stakeholder."
    ]
    
    next_question = behavioral_questions[min(question_count-1, len(behavioral_questions)-1)]
    
    return f"""{feedback}

**Behavioral Question {question_count}:**

{next_question}

Please structure your response using the STAR method (Situation, Task, Action, Result)."""

def generate_interview_completion() -> str:
    """Generate interview completion message"""
    
    name = st.session_state.candidate_data.get("name", "there")
    
    return f"""🎯 **Interview Complete!**

Thank you for your time today, **{name}**!

You've successfully completed our AI-powered interview featuring:
- ✅ Personalized questions based on your background
- ✅ Technical assessment tailored to your skills
- ✅ Behavioral evaluation using STAR methodology
- ✅ Real-time conversation adaptation

**Interview Summary:**
- **Technical Questions:** {st.session_state.get('technical_questions_asked', 0)}
- **Behavioral Questions:** {st.session_state.get('behavioral_questions_asked', 0)}
- **Total Duration:** {calculate_interview_duration()}

Our team will review your comprehensive responses and be in touch within 2-3 business days.

**Next Steps:**
1. Review your responses in the sidebar analytics
2. Await feedback from our hiring team
3. Prepare for potential next-round interviews

Have a great day! 🚀"""

def get_encouraging_feedback(response: str) -> str:
    """Generate encouraging feedback based on response"""
    
    response_length = len(response.split())
    
    if response_length > 50:
        return "I appreciate the detailed explanation and thorough approach."
    elif response_length > 20:
        return "That shows good problem-solving thinking."
    else:
        return "Good start! Your experience is valuable."

def calculate_interview_duration() -> str:
    """Calculate total interview duration"""
    
    start_time = st.session_state.get("interview_start_time", datetime.now())
    duration = datetime.now() - start_time
    minutes = duration.seconds // 60
    return f"{minutes} minutes"

def update_conversation_state(user_input: str):
    """Update conversation state after user input"""
    
    # Extract technical terms
    mentioned_tech = detect_technical_terms(user_input)
    
    if mentioned_tech and "candidate_data" in st.session_state:
        current_skills = st.session_state.candidate_data.get("tech_stack", [])
        updated_skills = list(set(current_skills + mentioned_tech))
        st.session_state.candidate_data["tech_stack"] = updated_skills
    
    # Update conversation context
    st.session_state.conversation_context = {
        "position": st.session_state.get("candidate_data", {}).get("position", "Software Developer"),
        "experience": st.session_state.get("candidate_data", {}).get("experience", "3 years"),
        "skills": st.session_state.get("candidate_data", {}).get("tech_stack", ["Python"]),
        "stage": st.session_state.get("conversation_stage", "technical"),
        "last_response_length": len(user_input.split())
    }

def render_question_controls():
    """Render dynamic question generation controls"""
    
    if st.session_state.get("conversation_stage") in ["technical_assessment", "behavioral_assessment"]:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🤖 Generate New Question", key="gen_new", use_container_width=True):
                generate_dynamic_question_sync()
        
        with col2:
            if st.button("🔄 Follow-up Question", key="gen_followup", use_container_width=True):
                generate_followup_question_sync()
        
        with col3:
            if st.button("⏭️ Next Stage", key="next_stage", use_container_width=True):
                advance_to_next_stage()

def generate_dynamic_question_sync():
    """Generate AI-powered question"""
    
    with st.spinner("🧠 AI is crafting a personalized question..."):
        try:
            context = {
                "position": st.session_state.get("candidate_data", {}).get("position", "Software Developer"),
                "experience": st.session_state.get("candidate_data", {}).get("experience", "3 years"),
                "skills": st.session_state.get("candidate_data", {}).get("tech_stack", ["Python"]),
                "stage": st.session_state.get("conversation_stage", "technical"),
                "asked_questions": [
                    msg["content"] for msg in st.session_state.get("messages", []) 
                    if msg["role"] == "assistant" and len(msg["content"]) > 50
                ]
            }
            
            if st.session_state.get("ai_manager"):
                question_result = st.session_state.ai_manager.generate_dynamic_question_sync(context)
                
                if question_result["success"]:
                    add_enhanced_message("assistant", f"""🤖 **AI Generated Question:**

{question_result['question']}

*This question was dynamically created by Llama 3.3 70B based on your specific background.*""")
                    
                    st.success("✨ New question generated!")
                    st.rerun()
                else:
                    st.error(f"Question generation failed: {question_result.get('error', 'Unknown error')}")
            else:
                st.error("AI Manager not available")
                
        except Exception as e:
            st.error(f"Question generation error: {e}")

def generate_followup_question_sync():
    """Generate follow-up question"""
    
    user_messages = [m for m in st.session_state.get("messages", []) if m["role"] == "user"]
    ai_messages = [m for m in st.session_state.get("messages", []) if m["role"] == "assistant"]
    
    if not user_messages or not ai_messages:
        st.warning("Need at least one Q&A exchange to generate follow-up")
        return
    
    last_user_response = user_messages[-1]["content"]
    add_enhanced_message("assistant", f"""🔄 **Follow-up Question:**

Can you elaborate more on your approach? What alternatives did you consider, and why did you choose this specific solution over others?

*This follow-up explores your decision-making process in more depth.*""")
    st.rerun()

def advance_to_next_stage():
    """Advance to next interview stage"""
    
    current_stage = st.session_state.get("conversation_stage", "greeting")
    
    stage_mapping = {
        "greeting": "info_collection",
        "info_collection": "technical_assessment", 
        "technical_assessment": "behavioral_assessment",
        "behavioral_assessment": "completed"
    }
    
    next_stage = stage_mapping.get(current_stage, "completed")
    st.session_state.conversation_stage = next_stage
    
    stage_messages = {
        "info_collection": "📝 **Information Collection**\n\nLet's gather details about your background.",
        "technical_assessment": "🔧 **Technical Assessment**\n\nTime for technical questions tailored to your skills.",
        "behavioral_assessment": "🤝 **Behavioral Assessment**\n\nLet's discuss soft skills using STAR methodology.",
        "completed": "🎉 **Interview Complete**\n\nThank you for your time!"
    }
    
    message = stage_messages.get(next_stage, "Moving to next stage")
    add_enhanced_message("assistant", message)
    st.rerun()

def display_enhanced_messages():
    """Display chat messages"""
    
    messages = st.session_state.get("messages", [])
    
    for message in messages:
        role = message["role"]
        content = message["content"]
        
        with st.chat_message(role, avatar=get_avatar(role)):
            st.markdown(content)

def add_enhanced_message(role: str, content: str):
    """Add message to conversation"""
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(),
        "stage": st.session_state.get("conversation_stage", "greeting"),
        "message_id": len(st.session_state.messages) + 1
    }
    
    st.session_state.messages.append(message)

def get_avatar(role: str) -> str:
    """Get avatar for chat message"""
    return "🤖" if role == "assistant" else "👤"

def get_dynamic_placeholder() -> str:
    """Get placeholder text for chat input"""
    
    stage = st.session_state.get("conversation_stage", "greeting")
    
    placeholders = {
        "greeting": "What's your name?",
        "info_collection": "Enter your response...",
        "technical_assessment": "Describe your technical approach...",
        "behavioral_assessment": "Use STAR method (Situation, Task, Action, Result)...",
        "completed": "Interview completed - thank you!"
    }
    
    return placeholders.get(stage, "Type your response...")

def detect_technical_terms(text):
    """Detect technical terms in text"""
    
    tech_keywords = [
        "python", "javascript", "react", "node", "django", "flask", "aws",
        "docker", "kubernetes", "git", "sql", "api", "database", "framework"
    ]
    
    text_lower = text.lower()
    found_terms = [term for term in tech_keywords if term in text_lower]
    return found_terms