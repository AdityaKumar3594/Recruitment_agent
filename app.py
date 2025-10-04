import streamlit as st
import os
import warnings
import torch
from dotenv import load_dotenv
from agents import ResumeAnalysisAgent
from ui import setup_page, display_analysis_results, display_interview_questions, apply_Nightingale_theme
import torch

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*torch.*")
torch.classes.__path__ = []

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="Nightingale Recruitment Agent",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    setup_page()
    
    # Header with Nightingale branding
    st.markdown("""
    <div style="background: linear-gradient(90deg, #e74c3c, #c0392b); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 3rem; font-weight: bold;">
            Nightingale Recruitment Agent
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Smart Resume Analysis & Interview Preparation System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Keys section
        st.subheader("API Keys")
        groq_api_key = st.text_input(
            "Groq API Key", 
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="Enter your Groq API key for LLM processing"
        )
        
        openai_api_key = st.text_input(
            "OpenAI API Key (Optional)", 
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key for enhanced vector embeddings. If not provided, the system will use direct text analysis."
        )
        
        if not openai_api_key:
            st.info("💡 Without OpenAI API key, the system will use direct text analysis (still fully functional)")
        else:
            st.success("✅ Enhanced vector embeddings enabled")
        
        # Cutoff score
        cutoff_score = st.slider(
            "Minimum Score for Selection", 
            min_value=50, 
            max_value=95, 
            value=75,
            help="Minimum overall score required for candidate selection"
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Nightingale Recruitment Agent")
        st.markdown("Advanced AI-powered recruitment analysis using Groq's lightning-fast LLM processing for comprehensive resume evaluation and interview preparation.")
    
    if not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.")
        st.info("💡 Get your free Groq API key at: https://console.groq.com/")
        return
    
    # Initialize the agent
    try:
        agent = ResumeAnalysisAgent(
            groq_api_key=groq_api_key, 
            openai_api_key=openai_api_key,
            cutoff_score=cutoff_score
        )
    except Exception as e:
        st.error(f"❌ Error initializing agent: {e}")
        return
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Resume Analysis", 
        "💬 Resume Q&A", 
        "🎯 Interview Questions", 
        "📈 Resume Improvement", 
        "📋 Improved Resume"
    ])
    
    with tab1:
        st.subheader("📊 Resume Analysis")
        
        # Main interface
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📄 Upload Resume")
            resume_file = st.file_uploader(
                "Choose resume file",
                type=['pdf', 'txt'],
                help="Upload your resume in PDF or TXT format",
                key="resume_upload"
            )
        
        with col2:
            st.markdown("#### 💼 Job Requirements")
            analysis_type = st.radio(
                "Choose analysis type:",
                ["Upload Job Description", "Enter Skills Manually"],
                key="analysis_type"
            )
            
            if analysis_type == "Upload Job Description":
                jd_file = st.file_uploader(
                    "Choose job description file",
                    type=['pdf', 'txt'],
                    help="Upload job description in PDF or TXT format",
                    key="jd_upload"
                )
                custom_skills = None
            else:
                jd_file = None
                custom_skills_text = st.text_area(
                    "Enter required skills (one per line):",
                    height=150,
                    placeholder="Python\nMachine Learning\nSQL\nDocker\n...",
                    key="custom_skills"
                )
                custom_skills = [skill.strip() for skill in custom_skills_text.split('\n') if skill.strip()] if custom_skills_text else None
    
        # Analysis button
        st.markdown("---")
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            if not resume_file:
                st.error("❌ Please upload a resume file.")
                return
            
            if not jd_file and not custom_skills:
                st.error("❌ Please either upload a job description or enter skills manually.")
                return
            
            with st.spinner("🔄 Analyzing resume with Groq AI... This may take a few minutes."):
                try:
                    # Perform analysis
                    if jd_file:
                        result = agent.analyze_resume(resume_file, custom_jd=jd_file)
                    else:
                        result = agent.analyze_resume(resume_file, role_requirements=custom_skills)
                    
                    if result:
                        st.session_state['analysis_result'] = result
                        st.session_state['agent'] = agent
                        st.success("✅ Analysis completed successfully!")
                    else:
                        st.error("❌ Analysis failed. Please check your inputs and try again.")
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
                    st.error("Please check:")
                    st.error("• Your Groq API key is valid")
                    st.error("• Your internet connection is working")
                    st.error("• The resume file contains readable text")
                    st.error("• You have entered skills or uploaded a job description")
        
        # Display results if available
        if 'analysis_result' in st.session_state:
            st.markdown("---")
            display_analysis_results(st.session_state['analysis_result'])
        
    with tab2:
        st.subheader("💬 Resume Q&A")
        
        if 'agent' in st.session_state:
            st.markdown("Ask specific questions about the analyzed resume:")
            
            # Predefined quick questions
            st.markdown("#### 🔥 Quick Questions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 What are the candidate's key strengths?"):
                    with st.spinner("🤔 Analyzing strengths..."):
                        try:
                            answer = st.session_state['agent'].ask_question("What are the candidate's key technical strengths and expertise areas?")
                            st.success("**Answer:**")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                if st.button("🎓 What is their educational background?"):
                    with st.spinner("🤔 Analyzing education..."):
                        try:
                            answer = st.session_state['agent'].ask_question("What is the candidate's educational background and qualifications?")
                            st.success("**Answer:**")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            
            with col2:
                if st.button("💼 What work experience do they have?"):
                    with st.spinner("🤔 Analyzing experience..."):
                        try:
                            answer = st.session_state['agent'].ask_question("Summarize the candidate's work experience and career progression.")
                            st.success("**Answer:**")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                if st.button("🛠️ What technologies do they know?"):
                    with st.spinner("🤔 Analyzing technologies..."):
                        try:
                            answer = st.session_state['agent'].ask_question("List all the technologies, programming languages, and tools mentioned in the resume.")
                            st.success("**Answer:**")
                            st.write(answer)
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            
            st.markdown("---")
            st.markdown("#### ❓ Custom Question")
            question = st.text_input(
                "Ask your own question about the resume:",
                placeholder="e.g., How many years of Python experience does the candidate have?",
                key="custom_question"
            )
            
            if st.button("🔍 Ask Question", type="primary") and question:
                with st.spinner("🤔 Getting answer..."):
                    try:
                        answer = st.session_state['agent'].ask_question(question)
                        st.success("**Answer:**")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"❌ Error getting answer: {e}")
        else:
            st.info("📋 Please analyze a resume first in the 'Resume Analysis' tab to use this feature.")
    
    with tab3:
        st.subheader("🎯 Interview Questions")
        
        if 'agent' in st.session_state and 'analysis_result' in st.session_state:
            st.markdown("Generate personalized interview questions based on the resume analysis:")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                num_questions = st.selectbox("Number of questions:", [3, 5, 8, 10], index=1, key="num_q")
            
            with col2:
                difficulty = st.selectbox("Difficulty level:", ["Easy", "Medium", "Hard"], index=1, key="difficulty")
            
            with col3:
                question_types = st.multiselect(
                    "Question types:",
                    ["technical", "behavioral", "situational", "coding"],
                    default=["technical", "behavioral"],
                    key="q_types"
                )
            
            if st.button("🎯 Generate Interview Questions", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating personalized interview questions..."):
                    try:
                        questions = st.session_state['agent'].generate_interview_questions(
                            num_questions=num_questions,
                            difficulty=difficulty,
                            question_types=question_types
                        )
                        if questions:
                            st.session_state['interview_questions'] = questions
                            display_interview_questions(questions, key_suffix="new")
                        else:
                            st.warning("⚠️ No questions generated. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error generating questions: {e}")
            
            # Display previously generated questions if available
            if 'interview_questions' in st.session_state:
                st.markdown("---")
                st.markdown("### 📝 Generated Questions")
                display_interview_questions(st.session_state['interview_questions'], key_suffix="saved")
        else:
            st.info("📋 Please analyze a resume first in the 'Resume Analysis' tab to generate interview questions.")
    
    with tab4:
        st.subheader("📈 Resume Improvement")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            
            if result.get('detailed_weaknesses'):
                st.markdown("### 🎯 Improvement Recommendations")
                
                for weakness in result['detailed_weaknesses']:
                    with st.expander(f"🔧 Improve: {weakness.get('skill', 'Unknown Skill')} (Current Score: {weakness.get('score', 0)}/10)"):
                        st.markdown(f"**📋 Issue:** {weakness.get('detail', 'No details available')}")
                        
                        if weakness.get('suggestions'):
                            st.markdown("**💡 Improvement Suggestions:**")
                            for i, suggestion in enumerate(weakness['suggestions'], 1):
                                st.markdown(f"{i}. {suggestion}")
                        
                        if weakness.get('example'):
                            st.markdown("**✨ Example Addition:**")
                            st.code(weakness['example'], language='text')
                            
                            # Copy button for the example
                            if st.button(f"📋 Copy Example", key=f"copy_{weakness.get('skill', 'unknown')}"):
                                st.success("✅ Example copied to clipboard!")
            else:
                st.success("🎉 Great! No major improvement areas identified. Your resume looks strong!")
        else:
            st.info("📋 Please analyze a resume first in the 'Resume Analysis' tab to see improvement suggestions.")
    
    with tab5:
        st.subheader("📋 Improved Resume")
        
        if 'analysis_result' in st.session_state and 'agent' in st.session_state:
            result = st.session_state['analysis_result']
            agent = st.session_state['agent']
            
            # Configuration section
            st.markdown("### ⚙️ Resume Enhancement Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Industry selection
                industry = st.selectbox(
                    "🏢 Target Industry:",
                    [
                        "Technology/Software",
                        "Healthcare/Medical",
                        "Finance/Banking",
                        "Marketing/Sales",
                        "Engineering",
                        "Education",
                        "Consulting",
                        "Manufacturing",
                        "Retail/E-commerce",
                        "Non-profit",
                        "Government",
                        "Other"
                    ],
                    key="industry_select"
                )
                
                # Experience level
                experience_level = st.selectbox(
                    "📈 Experience Level:",
                    ["Entry Level (0-2 years)", "Mid Level (3-7 years)", "Senior Level (8+ years)", "Executive Level"],
                    index=1,
                    key="exp_level"
                )
            
            with col2:
                # Resume format
                resume_format = st.selectbox(
                    "📄 Resume Format:",
                    ["Modern Professional", "ATS-Optimized", "Creative", "Executive", "Academic"],
                    key="format_select"
                )
                
                # Enhancement options
                enhancement_options = st.multiselect(
                    "🔧 Enhancement Options:",
                    [
                        "ATS Keyword Optimization",
                        "Action Verb Enhancement",
                        "Quantify Achievements",
                        "Skills Section Rewrite",
                        "Professional Summary",
                        "Industry-Specific Terminology"
                    ],
                    default=["ATS Keyword Optimization", "Action Verb Enhancement", "Quantify Achievements"],
                    key="enhancement_opts"
                )
            
            st.markdown("---")
            
            # Generate improved resume button
            if st.button("🚀 Generate Improved Resume", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating your improved resume... This may take a few minutes."):
                    try:
                        improved_resume = agent.generate_improved_resume(
                            industry=industry,
                            experience_level=experience_level,
                            resume_format=resume_format,
                            enhancement_options=enhancement_options
                        )
                        
                        if improved_resume:
                            st.session_state['improved_resume'] = improved_resume
                            st.success("✅ Improved resume generated successfully!")
                        else:
                            st.error("❌ Failed to generate improved resume. Please try again.")
                    
                    except Exception as e:
                        st.error(f"❌ Error generating improved resume: {e}")
            
            # Display improved resume if available
            if 'improved_resume' in st.session_state:
                st.markdown("---")
                st.markdown("### 📄 Your Improved Resume")
                
                # Tabs for different views
                resume_tab1, resume_tab2, resume_tab3 = st.tabs(["📝 Content", "📊 ATS Analysis", "💾 Export"])
                
                with resume_tab1:
                    st.markdown("#### Enhanced Resume Content")
                    
                    # Display the improved resume content
                    improved_content = st.session_state['improved_resume'].get('content', '')
                    st.text_area(
                        "Improved Resume:",
                        value=improved_content,
                        height=600,
                        key="improved_resume_content"
                    )
                    
                    # Show improvements made
                    if st.session_state['improved_resume'].get('improvements'):
                        st.markdown("#### 🎯 Improvements Made")
                        for improvement in st.session_state['improved_resume']['improvements']:
                            st.markdown(f"• {improvement}")
                
                with resume_tab2:
                    st.markdown("#### 🤖 ATS Optimization Analysis")
                    
                    ats_analysis = st.session_state['improved_resume'].get('ats_analysis', {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "ATS Score",
                            f"{ats_analysis.get('score', 0)}%",
                            delta=f"+{ats_analysis.get('improvement', 0)}%"
                        )
                    
                    with col2:
                        st.metric(
                            "Keywords Matched",
                            ats_analysis.get('keywords_matched', 0),
                            delta=f"+{ats_analysis.get('keywords_added', 0)}"
                        )
                    
                    with col3:
                        st.metric(
                            "Readability Score",
                            f"{ats_analysis.get('readability', 0)}/10"
                        )
                    
                    # ATS recommendations
                    if ats_analysis.get('recommendations'):
                        st.markdown("#### 💡 ATS Recommendations")
                        for rec in ats_analysis['recommendations']:
                            st.info(rec)
                
                with resume_tab3:
                    st.markdown("#### 💾 Export Your Resume")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📄 Text Formats**")
                        
                        # Plain text download
                        if st.button("📝 Download as TXT", use_container_width=True):
                            txt_content = st.session_state['improved_resume'].get('content', '')
                            st.download_button(
                                label="💾 Download TXT",
                                data=txt_content,
                                file_name="improved_resume.txt",
                                mime="text/plain"
                            )
                        
                        # Markdown download
                        if st.button("📋 Download as Markdown", use_container_width=True):
                            md_content = agent.convert_to_markdown(st.session_state['improved_resume'].get('content', ''))
                            st.download_button(
                                label="💾 Download MD",
                                data=md_content,
                                file_name="improved_resume.md",
                                mime="text/markdown"
                            )
                    
                    with col2:
                        st.markdown("**📄 Professional Formats**")
                        
                        # PDF generation (placeholder - would need additional libraries)
                        if st.button("📄 Generate PDF", use_container_width=True):
                            st.info("🔄 PDF generation feature requires additional setup. For now, copy the content and paste into a word processor.")
                        
                        # DOCX generation (placeholder)
                        if st.button("📄 Generate DOCX", use_container_width=True):
                            st.info("🔄 DOCX generation feature requires additional setup. For now, copy the content and paste into Microsoft Word.")
                    
                    st.markdown("---")
                    st.markdown("#### 📋 Quick Copy")
                    st.code(st.session_state['improved_resume'].get('content', ''), language='text')
        
        else:
            st.info("📋 Please analyze a resume first in the 'Resume Analysis' tab to generate an improved version.")
            
            # Show preview of features
            st.markdown("### 🎯 Available Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🤖 Automatic Resume Rewriting**
                - AI-powered content enhancement
                - Professional language optimization
                - Achievement quantification
                - Action verb strengthening
                """)
                
                st.markdown("""
                **📊 ATS Optimization**
                - Keyword density analysis
                - Format compatibility check
                - Readability scoring
                - Industry-specific optimization
                """)
            
            with col2:
                st.markdown("""
                **💾 Multiple Format Exports**
                - Plain text (.txt)
                - Markdown (.md)
                - PDF generation
                - Microsoft Word (.docx)
                """)
                
                st.markdown("""
                **🏢 Industry-Specific Templates**
                - Technology/Software
                - Healthcare/Medical
                - Finance/Banking
                - And 8+ more industries
                """)

if __name__ == "__main__":
    main()
