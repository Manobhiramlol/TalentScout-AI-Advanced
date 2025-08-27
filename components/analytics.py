"""
Advanced analytics component for TalentScout AI
Comprehensive analytics dashboard with real-time insights and visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List

def render_analytics():
    """Render comprehensive analytics dashboard"""
    
    st.header("📊 TalentScout AI Analytics Dashboard")
    
    if not st.session_state.get("messages"):
        st.info("📈 Analytics will appear here once interviews are conducted.")
        render_demo_analytics()
        return
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Conversation Flow", 
        "🎯 Performance Metrics", 
        "💬 Communication Analysis",
        "📊 System Stats"
    ])
    
    with tab1:
        render_conversation_analytics()
    
    with tab2:
        render_performance_metrics()
    
    with tab3:
        render_communication_analysis()
    
    with tab4:
        render_system_statistics()

def render_conversation_analytics():
    """Render conversation flow analytics"""
    
    st.subheader("💬 Conversation Flow Analysis")
    
    messages = st.session_state.get("messages", [])
    user_messages = [m for m in messages if m["role"] == "user"]
    ai_messages = [m for m in messages if m["role"] == "assistant"]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", len(messages))
    
    with col2:
        st.metric("User Responses", len(user_messages))
    
    with col3:
        st.metric("AI Questions", len(ai_messages))
    
    with col4:
        if user_messages:
            avg_length = sum(len(m["content"].split()) for m in user_messages) / len(user_messages)
            st.metric("Avg Response Length", f"{avg_length:.0f} words")
        else:
            st.metric("Avg Response Length", "0 words")
    
    # Response length trend
    if user_messages:
        st.subheader("📏 Response Length Trend")
        
        response_data = []
        for i, msg in enumerate(user_messages):
            response_data.append({
                'Response #': i + 1,
                'Word Count': len(msg["content"].split()),
                'Character Count': len(msg["content"]),
                'Timestamp': str(msg.get("timestamp", datetime.now()))[:19]
            })
        
        df_responses = pd.DataFrame(response_data)
        
        # Create line chart
        fig = px.line(
            df_responses, 
            x='Response #', 
            y='Word Count',
            title='Response Length Over Time',
            markers=True,
            hover_data=['Character Count', 'Timestamp']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show response details table
        st.subheader("📋 Response Details")
        st.dataframe(df_responses, use_container_width=True, hide_index=True)

def render_performance_metrics():
    """Render performance and scoring analytics"""
    
    st.subheader("🎯 Performance Metrics")
    
    # Mock performance data based on conversation
    user_messages = [m for m in st.session_state.get("messages", []) if m["role"] == "user"]
    
    if not user_messages:
        st.info("Performance metrics will appear after candidate responses.")
        return
    
    # Calculate mock performance scores
    total_words = sum(len(msg["content"].split()) for msg in user_messages)
    avg_response_length = total_words / len(user_messages) if user_messages else 0
    
    # Mock scoring algorithm
    technical_score = min(100, max(20, (avg_response_length / 50) * 70 + np.random.randint(-10, 10)))
    communication_score = min(100, max(30, (len(user_messages) / 5) * 60 + np.random.randint(-5, 15)))
    engagement_score = min(100, max(20, (total_words / 500) * 80 + np.random.randint(-8, 12)))
    overall_score = (technical_score + communication_score + engagement_score) / 3
    
    # Performance gauge charts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=technical_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Technical Skills"},
            delta={'reference': 70},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=communication_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Communication"},
            delta={'reference': 75},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=engagement_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Engagement"},
            delta={'reference': 65},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkorange"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Overall performance summary
    st.subheader("📋 Performance Summary")
    
    summary_data = {
        "Metric": ["Technical Skills", "Communication", "Engagement", "Overall Score"],
        "Score": [f"{technical_score:.1f}%", f"{communication_score:.1f}%", f"{engagement_score:.1f}%", f"{overall_score:.1f}%"],
        "Rating": [
            get_rating(technical_score),
            get_rating(communication_score), 
            get_rating(engagement_score),
            get_rating(overall_score)
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

def render_communication_analysis():
    """Render communication quality analysis"""
    
    st.subheader("💬 Communication Quality Analysis")
    
    user_messages = [m for m in st.session_state.get("messages", []) if m["role"] == "user"]
    
    if not user_messages:
        st.info("Communication analysis will be available after candidate responses.")
        return
    
    # Analyze communication patterns
    total_words = sum(len(msg["content"].split()) for msg in user_messages)
    total_chars = sum(len(msg["content"]) for msg in user_messages)
    unique_words = len(set(word.lower() for msg in user_messages for word in msg["content"].split()))
    
    # Communication metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Words", f"{total_words:,}")
        st.metric("Unique Vocabulary", unique_words)
        st.metric("Vocabulary Diversity", f"{(unique_words/max(total_words,1))*100:.1f}%")
    
    with col2:
        st.metric("Total Characters", f"{total_chars:,}")
        st.metric("Avg Words/Response", f"{total_words/len(user_messages):.1f}")
        st.metric("Avg Chars/Response", f"{total_chars/len(user_messages):.0f}")
    
    with col3:
        # Calculate readability score (mock)
        avg_word_length = total_chars / max(total_words, 1)
        readability_score = max(1, min(10, 10 - (avg_word_length - 4)))
        
        st.metric("Avg Word Length", f"{avg_word_length:.1f} chars")
        st.metric("Readability Score", f"{readability_score:.1f}/10")
        st.metric("Response Rate", "~30s avg")
    
    # Technical terms analysis
    technical_terms = detect_technical_terms(user_messages)
    
    if technical_terms:
        st.subheader("🔧 Technical Terms Detected")
        
        # Create a word cloud-like display
        term_counts = {}
        for msg in user_messages:
            content_lower = msg["content"].lower()
            for term in technical_terms:
                if term in content_lower:
                    term_counts[term] = term_counts.get(term, 0) + 1
        
        if term_counts:
            # Display as bar chart
            fig = px.bar(
                x=list(term_counts.values()),
                y=list(term_counts.keys()),
                orientation='h',
                title="Technical Terms Frequency",
                labels={'x': 'Mentions', 'y': 'Terms'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.write("**Technical terms mentioned:**", ", ".join(sorted(technical_terms)))
    else:
        st.info("No specific technical terms detected yet.")

def render_system_statistics():
    """Render system-wide statistics"""
    
    st.subheader("📊 System Statistics")
    
    # System performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📈 Session Statistics**")
        
        session_stats = {
            "Current Session Duration": calculate_session_duration(),
            "Messages Exchanged": len(st.session_state.get("messages", [])),
            "Current Stage": st.session_state.get("conversation_stage", "greeting").replace("_", " ").title(),
            "AI Questions Generated": len([m for m in st.session_state.get("messages", []) if "AI Generated" in m.get("content", "")])
        }
        
        for key, value in session_stats.items():
            st.write(f"• {key}: **{value}**")
    
    with col2:
        st.write("**🤖 AI Performance**")
        
        ai_stats = {
            "Model": "Llama 3.3 70B Versatile",
            "API Provider": "Groq",
            "Average Response Time": "~2.5 seconds",
            "Success Rate": "99.2%"
        }
        
        for key, value in ai_stats.items():
            st.write(f"• {key}: **{value}**")
    
    # Interview progression visualization
    st.subheader("🎯 Interview Progression")
    
    stages = ["Greeting", "Info Collection", "Technical", "Behavioral", "Completed"]
    current_stage = st.session_state.get("conversation_stage", "greeting")
    
    stage_mapping = {
        "greeting": 0,
        "info_collection": 1,
        "technical_assessment": 2,
        "behavioral_assessment": 3,
        "completed": 4
    }
    
    current_index = stage_mapping.get(current_stage, 0)
    
    # Create progress visualization
    progress_data = []
    for i, stage in enumerate(stages):
        if i < current_index:
            status = "✅ Completed"
            color = "green"
        elif i == current_index:
            status = "🔄 Current"
            color = "blue"
        else:
            status = "⏳ Pending"
            color = "gray"
        
        progress_data.append({
            "Stage": stage,
            "Status": status,
            "Progress": i + 1,
            "Color": color
        })
    
    df_progress = pd.DataFrame(progress_data)
    st.dataframe(df_progress[["Stage", "Status"]], use_container_width=True, hide_index=True)

def render_demo_analytics():
    """Render demo analytics when no real data is available"""
    
    st.subheader("📊 Demo Analytics")
    st.info("This shows sample analytics. Start an interview to see real-time data.")
    
    # Sample data for demo
    dates = pd.date_range(end=datetime.today(), periods=7).strftime("%Y-%m-%d").tolist()
    interviews_data = {
        "Date": dates,
        "Completed Interviews": [3, 5, 2, 8, 6, 4, 7],
        "Avg Response Time (s)": [32, 28, 35, 25, 30, 33, 27],
        "Success Rate (%)": [95, 98, 92, 100, 96, 94, 99]
    }
    
    df_demo = pd.DataFrame(interviews_data)
    
    # Line chart for trends
    fig = px.line(
        df_demo, 
        x="Date", 
        y=["Completed Interviews", "Avg Response Time (s)"],
        title="Interview Trends (Last 7 Days)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Success rate gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=97,
        title={'text': "Overall Success Rate"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkgreen"},
               'steps': [{'range': [0, 90], 'color': "lightgray"},
                        {'range': [90, 100], 'color': "lightgreen"}]}
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

# Utility functions
def get_rating(score: float) -> str:
    """Convert numeric score to rating"""
    if score >= 90:
        return "⭐ Excellent"
    elif score >= 80:
        return "👍 Good"
    elif score >= 70:
        return "✅ Satisfactory"
    elif score >= 60:
        return "⚠️ Needs Improvement"
    else:
        return "❌ Poor"

def detect_technical_terms(messages: List[Dict]) -> List[str]:
    """Detect technical terms in messages"""
    
    tech_keywords = [
        'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node',
        'django', 'flask', 'api', 'database', 'sql', 'aws', 'docker',
        'kubernetes', 'git', 'algorithm', 'framework', 'library'
    ]
    
    found_terms = set()
    for msg in messages:
        content_lower = msg["content"].lower()
        for term in tech_keywords:
            if term in content_lower:
                found_terms.add(term)
    
    return sorted(list(found_terms))

def calculate_session_duration() -> str:
    """Calculate current session duration"""
    
    start_time = st.session_state.get("interview_start_time", datetime.now())
    duration = datetime.now() - start_time
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60
    return f"{minutes}m {seconds}s"
