import streamlit as st
import pandas as pd
import base64
import io
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
    /* Nightingale Theme Colors */
    :root {
        --Nightingale-red: #e74c3c;
        --Nightingale-dark-red: #c0392b;
        --Nightingale-light-red: #f1c0c0;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: var(--Nightingale-red);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--Nightingale-red);
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .skill-high {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.1rem;
        display: inline-block;
        font-weight: 500;
    }
    
    .skill-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.1rem;
        display: inline-block;
        font-weight: 500;
    }
    
    .skill-low {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.1rem;
        display: inline-block;
        font-weight: 500;
    }
    
    .weakness-card {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .strength-card {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .question-card {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        color: #495057;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--Nightingale-red) !important;
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, var(--Nightingale-red), var(--Nightingale-dark-red));
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def apply_Nightingale_theme():
    """Apply the Nightingale Recruitment Agent theme."""
    apply_custom_css()

def setup_page():
    """Setup the main page configuration and styling."""
    apply_Nightingale_theme()

def display_score_gauge(score, title="Overall Score"):
    """Display a gauge chart for the overall score."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20, 'color': '#e74c3c'}},
        delta = {'reference': 75},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': '#e74c3c'},
            'bar': {'color': "#e74c3c"},
            'steps': [
                {'range': [0, 50], 'color': "#f8d7da"},
                {'range': [50, 75], 'color': "#fff3cd"},
                {'range': [75, 100], 'color': "#d4edda"}
            ],
            'threshold': {
                'line': {'color': "#c0392b", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': '#2c3e50'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def display_skills_chart(skills_scores):
    """Display a horizontal bar chart of skills scores."""
    if not skills_scores:
        return None
    
    skills = list(skills_scores.keys())
    scores = list(skills_scores.values())
    
    # Create color mapping based on score with Nightingale theme
    colors = ['#e74c3c' if score <= 5 else '#f39c12' if score <= 7 else '#27ae60' for score in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            y=skills,
            x=scores,
            orientation='h',
            marker_color=colors,
            text=scores,
            textposition='auto',
            textfont={'color': 'white', 'size': 12},
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Skills Assessment Scores",
            'font': {'size': 18, 'color': '#e74c3c'},
            'x': 0.5
        },
        xaxis_title="Score (0-10)",
        yaxis_title="Skills",
        height=max(400, len(skills) * 30),
        showlegend=False,
        font={'color': '#2c3e50'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'gridcolor': '#ecf0f1'},
        yaxis={'gridcolor': '#ecf0f1'}
    )
    
    return fig

def display_analysis_results(result):
    """Display the complete analysis results."""
    if not result:
        st.error("No analysis results to display.")
        return
    
    # Overall Score Section
    st.subheader("📊 Overall Assessment")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Display gauge chart
        gauge_fig = display_score_gauge(result.get('overall_score', 0))
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col2:
        st.metric(
            label="Overall Score",
            value=f"{result.get('overall_score', 0)}%",
            delta=f"{result.get('overall_score', 0) - 75}% vs threshold"
        )
    
    with col3:
        selection_status = "✅ SELECTED" if result.get('selected', False) else "❌ NOT SELECTED"
        st.markdown(f"### {selection_status}")
        
        if result.get('selected', False):
            st.success("Candidate meets the requirements!")
        else:
            st.warning("Candidate needs improvement in key areas.")
    
    # Skills Breakdown
    st.subheader("🎯 Skills Analysis")
    
    if result.get('skills_scores'):
        # Display skills chart
        skills_fig = display_skills_chart(result['skills_scores'])
        if skills_fig:
            st.plotly_chart(skills_fig, use_container_width=True)
        
        # Skills summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💪 Strengths")
            strengths = [skill for skill, score in result['skills_scores'].items() if score > 7]
            if strengths:
                for skill in strengths:
                    score = result['skills_scores'][skill]
                    st.markdown(f'<div class="skill-high">{skill}: {score}/10</div>', unsafe_allow_html=True)
            else:
                st.info("No strong skills identified.")
        
        with col2:
            st.markdown("#### ⚠️ Areas for Improvement")
            weaknesses = [skill for skill, score in result['skills_scores'].items() if score <= 5]
            if weaknesses:
                for skill in weaknesses:
                    score = result['skills_scores'][skill]
                    st.markdown(f'<div class="skill-low">{skill}: {score}/10</div>', unsafe_allow_html=True)
            else:
                st.success("No major weaknesses identified!")
    
    # Detailed Weaknesses
    if result.get('detailed_weaknesses'):
        st.subheader("🔍 Detailed Improvement Areas")
        
        for weakness in result['detailed_weaknesses']:
            with st.expander(f"📌 {weakness.get('skill', 'Unknown Skill')} (Score: {weakness.get('score', 0)}/10)"):
                st.markdown(f"**Issue:** {weakness.get('detail', 'No details available')}")
                
                if weakness.get('suggestions'):
                    st.markdown("**Improvement Suggestions:**")
                    for suggestion in weakness['suggestions']:
                        st.markdown(f"• {suggestion}")
                
                if weakness.get('example'):
                    st.markdown("**Example Addition:**")
                    st.code(weakness['example'], language='text')
    
    # Skills Reasoning (collapsible)
    if result.get('skill_reasoning'):
        with st.expander("📋 Detailed Skills Reasoning"):
            for skill, reasoning in result['skill_reasoning'].items():
                st.markdown(f"**{skill}:** {reasoning}")

def display_interview_questions(questions, key_suffix=""):
    """Display generated interview questions."""
    if not questions:
        st.warning("No interview questions generated.")
        return
    
    st.subheader("🎯 Personalized Interview Questions")
    
    for i, question in enumerate(questions, 1):
        question_type = question.get('type', 'general').title()
        question_text = question.get('question', 'No question available')
        focus_area = question.get('focus_area', 'General')
        
        with st.expander(f"Question {i}: {question_type} - {focus_area}"):
            st.markdown(f"**Type:** {question_type}")
            st.markdown(f"**Focus Area:** {focus_area}")
            st.markdown(f"**Question:** {question_text}")
            
            # Add space for notes with unique key
            unique_key = f"notes_{i}_{key_suffix}" if key_suffix else f"notes_{i}_{hash(str(questions))}"
            st.text_area(
                f"Notes for Question {i}:",
                key=unique_key,
                height=100,
                placeholder="Add your preparation notes here..."
            )

def create_downloadable_report(result, questions=None):
    """Create a downloadable PDF report of the analysis."""
    # This is a placeholder for PDF generation functionality
    # You could implement this using libraries like reportlab or weasyprint
    pass

def display_comparison_chart(candidates_data):
    """Display comparison chart for multiple candidates."""
    # This is a placeholder for multi-candidate comparison
    # Could be implemented for batch processing
    pass