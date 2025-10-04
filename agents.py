import re 
import PyPDF2
import io
import tempfile
import os 
import json
from concurrent.futures import ThreadPoolExecutor

torch.classes.__path__ = []

# Try to import optional dependencies
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: langchain-groq not installed. Please install it with: pip install langchain-groq")

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: Some langchain packages not installed. Vector embeddings will be disabled.")

# Fallback imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class SimpleGroqClient:
    """Simple Groq API client for direct HTTP requests."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def invoke(self, prompt):
        if not REQUESTS_AVAILABLE:
            raise Exception("requests library not available")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
        
        try:
            print(f"Making API call to Groq...")
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                print(f"API Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                raise Exception(f"Invalid API response format: {result}")
            
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            
            content = result['choices'][0]['message']['content']
            print(f"API call successful, response length: {len(content)}")
            return MockResponse(content)
            
        except requests.exceptions.Timeout:
            raise Exception("API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
        except Exception as e:
            raise Exception(f"Groq API error: {e}")

class ResumeAnalysisAgent:
    def __init__(self, groq_api_key, openai_api_key=None, cutoff_score=75):
        self.groq_api_key = groq_api_key
        self.openai_api_key = openai_api_key or "dummy_key"
        self.cutoff_score = cutoff_score
        self.resume_text = None
        self.rag_vectorstore = None
        self.analysis_result = None
        self.jd_text = None
        self.extracted_skills = None
        self.resume_weaknesses = []
        self.resume_strengths = []
        self.improvement_suggestions = {}
        
        # Initialize LLM client
        if GROQ_AVAILABLE:
            self.llm_client = ChatGroq(model="openai/gpt-oss-120b", api_key=self.groq_api_key, temperature=0)
        elif REQUESTS_AVAILABLE:
            self.llm_client = SimpleGroqClient(self.groq_api_key)
        else:
            raise Exception("No suitable LLM client available. Please install langchain-groq or requests.")
        
        # Test the API connection
        self._test_api_connection()
    
    def _test_api_connection(self):
        """Test if the API key and connection work."""
        try:
            print("Testing API connection...")
            test_response = self.llm_client.invoke("Say 'API test successful'")
            if "successful" in test_response.content.lower():
                print("✅ API connection test passed")
            else:
                print("⚠️ API connection test returned unexpected response")
        except Exception as e:
            print(f"❌ API connection test failed: {e}")
            raise Exception(f"API connection failed: {e}")

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file."""

        try:
            if hasattr(pdf_file,'getvalue'):
                pdf_data=pdf_file.getvalue()
                pdf_file_like=io.BytesIO(pdf_data)
                reader = PyPDF2.PdfReader(pdf_file_like)
            else:
                reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""   
    def extract_text_from_txt(self, txt_file):
        """Extract text from a TXT file."""
        try:
            if hasattr(txt_file,'getvalue'):
                text=txt_file.getvalue().decode('utf-8')
            else:
                with open(txt_file, 'r', encoding='utf-8') as file:
                    text = file.read()
            return text
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ""
    
    def extract_text_from_file(self, file):
        """Extract text from a file based on its type."""
        if hasattr(file,'name'):
            file_extension = file.name.split('.')[-1].lower()
        else:
            file_extension = file.split('.')[-1].lower()
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file)

        else:
            print("Unsupported file format. Please upload a PDF or TXT file.")
            return ""
    
    def create_rag_vector_store(self, text):
        """Create a RAG vector store from the provided text."""
        if not LANGCHAIN_AVAILABLE:
            print("Warning: Langchain packages not available. Vector store creation skipped.")
            return None
            
        try:
            if not self.openai_api_key or self.openai_api_key == "dummy_key":
                print("Warning: No valid OpenAI API key provided. Vector store creation skipped.")
                return None
                
            text_splitter = RecursiveCharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len,)
            chunks = text_splitter.split_text(text)
            embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
            vectorstore = FAISS.from_texts(chunks, embeddings)
            return vectorstore
        except Exception as e:
            print(f"Error creating RAG vector store: {e}")
            return None
    
    def create_vector_store(self, text):
        """Create a vector store from the provided text."""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        try:
            text_splitter = RecursiveCharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len,)
            chunks = text_splitter.split_text(text)
            embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
            vectorstore = FAISS.from_texts(chunks, embeddings)
            return vectorstore
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return None
    
    def analyze_skill(self, qa_chain, skill):
        """Analyze a specific skill using the QA chain."""
        query = f"Does the resume mention the skill '{skill}'? Provide numeric rating on a scale of 0-10 ,followed by reasoning."
        result = qa_chain.run(query)
        match = re.search(r"(\d{1,2})", result)
        score = int(match.group(1)) if match else 0

        reasoning = result.split('.', 1)[1].strip() if '.' in result and len(result.split('.', 1)) > 1 else "No reasoning provided."
        return skill, min(score, 10), reasoning
    
    def direct_skill_analysis(self, resume_text, skills):
        """Perform direct skill analysis without vector store (fallback method)."""
        try:
            print(f"Starting direct skill analysis for {len(skills)} skills...")
            skills_scores = {}
            skill_reasoning = {}
            missing_skills = []
            total_score = 0
            
            for i, skill in enumerate(skills):
                print(f"Analyzing skill {i+1}/{len(skills)}: {skill}")
                
                prompt = f"""
                Analyze the following resume text for the skill '{skill}'. 
                Provide a numeric rating from 0-10 based on how well the resume demonstrates this skill.
                Consider:
                - Direct mentions of the skill
                - Related experience and projects
                - Depth of experience indicated
                
                Resume Text:
                {resume_text[:2000]}...
                
                Respond with only a number (0-10) followed by a brief explanation.
                Format: "Score: X - Explanation"
                """
                
                try:
                    response = self.llm_client.invoke(prompt)
                    result_text = response.content
                    print(f"Response for {skill}: {result_text[:100]}...")
                    
                    # Extract score
                    match = re.search(r"(\d{1,2})", result_text)
                    score = int(match.group(1)) if match else 0
                    score = min(score, 10)
                    
                    # Extract reasoning
                    reasoning = result_text.split('-', 1)[1].strip() if '-' in result_text else "Direct text analysis"
                    
                    skills_scores[skill] = score
                    skill_reasoning[skill] = reasoning
                    total_score += score
                    
                    if score <= 5:
                        missing_skills.append(skill)
                        
                    print(f"Score for {skill}: {score}/10")
                    
                except Exception as skill_error:
                    print(f"Error analyzing skill {skill}: {skill_error}")
                    # Assign default score if individual skill analysis fails
                    skills_scores[skill] = 0
                    skill_reasoning[skill] = f"Error analyzing skill: {skill_error}"
                    missing_skills.append(skill)
            
            if not skills_scores:
                print("No skills were successfully analyzed")
                return None
            
            overall_score = int((total_score / (len(skills) * 10)) * 100)
            selected = overall_score >= self.cutoff_score
            
            strengths = [skill for skill, score in skills_scores.items() if score > 7]
            improvement_areas = missing_skills if not selected else []
            
            self.resume_strengths = strengths
            
            print(f"Analysis complete. Overall score: {overall_score}%")
            
            return {
                "overall_score": overall_score,
                "skills_scores": skills_scores,
                "skill_reasoning": skill_reasoning,
                "selected": selected,
                "reasoning": "Candidate evaluated using direct text analysis (no vector embeddings)",
                "missing_skills": missing_skills,
                "improvement_areas": improvement_areas
            }
            
        except Exception as e:
            print(f"Error in direct skill analysis: {e}")
            import traceback
            traceback.print_exc()
            return None
    def analyze_resume_weaknesses(self):
        """Analyze the resume for weaknesses based on the job description."""
        if not self.resume_text or not self.extracted_skills or not self.analysis_result:
            return []
        weaknesses = []
        for skill in self.analysis_result.get('missing_skills', []):
            prompt= f"""
            Analyze why the resume is weak in demonstrating in "{skill}".
            For your analysis,consider:
            1.what is missing from the resume regarding this skill?
            2.How could it be improved with specific example?
            3.What specific action items would make this skill stand out?
            Resume Content: {self.resume_text[:3000]}...
            Provide your response in json format:
            {{
            "weakness":"A concise description of what's missing or problematic(1-2 sentences)",
            "improvement_suggestions":[
                "specific suggestion 1",
                    "specific suggestion 2",
                        "specific suggestion 3"],
            "example addition":"A specific bullet point that could be added to showcase this skill more effectively"
            }}
            Return only valid JSON,no other text.

            """
            response = self.llm_client.invoke(prompt)
            weakness_content = response.content
            try:
                weakness_data = json.loads(weakness_content)
                weakness_detail={
                    "skill":skill,
                    "score":self.analysis_result['skills_scores'].get(skill, 0),
                    "detail": weakness_data.get("weakness", "No specific details provided."),
                    "suggestions": weakness_data.get("improvement_suggestions", []),
                    "example": weakness_data.get("example_addition", "No specific example provided")
                }
                weaknesses.append(weakness_detail)

                self.improvement_suggestions[skill] = {
                    "suggestions": weakness_data.get("improvement_suggestions", []),
                    "example": weakness_data.get("example_addition", "No specific example provided")
                }
            except json.JSONDecodeError:
                weaknesses.append({
                    "skill": skill,
                    "score": self.analysis_result['skills_scores'].get(skill, 0),
                    "detail": weakness_content[:200] if weakness_content else "No details available"
                })
        self.resume_weaknesses = weaknesses
        return weaknesses
    def extract_skills_from_jd(self, jd_text):
        """Extract skills from the job description text."""
        try:
            prompt = f"""Extract a comprehensive list of technical skills,technology,and
            competencies from the following job description.
            Format the output as a Python list of strings.Only include the list,nothing else.
            Job Description: {jd_text}
            """
            response = self.llm_client.invoke(prompt)
            skills_text=response.content

            match=re.search(r"\[(.*?)\]", skills_text, re.DOTALL)
            if match:
                skills_text=match.group(0)
            try:
                skills_list = eval(skills_text)
                if isinstance(skills_list, list):
                    return skills_list
            except:
                pass

            skills=[]

            for line in skills_text.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    skill = line[2:].strip()
                    if skill:
                        skills.append(skill)
                elif line.startswith('"') and line.endswith('"'):
                    skill = line.strip('"')
                    if skill:
                        skills.append(skill)
            return skills
        except Exception as e:
            print(f"Error extracting skills from JD: {e}")
            return []
    
    def semantic_skill_analysis(self, resume_text, skills):
        """Perform semantic skill analysis on the resume text."""
        vectorstore = self.create_rag_vector_store(resume_text)
        
        # If vector store creation fails, use direct text analysis
        if vectorstore is None:
            return self.direct_skill_analysis(resume_text, skills)
            
        retriever = vectorstore.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm_client if GROQ_AVAILABLE else ChatGroq(model="openai/gpt-oss-120b", api_key=self.groq_api_key, temperature=0),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False
        )   
        skills_scores = {}
        skill_reasoning = {}
        missing_skills = []
        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            results=list(executor.map(lambda skill: self.analyze_skill(qa_chain, skill), skills))
        for skill, score, reasoning in results:
            skills_scores[skill] = score
            skill_reasoning[skill] = reasoning
            total_score += score
            if score <= 5:
                missing_skills.append(skill)
        overall_score=int((total_score / (len(skills) * 10)) * 100)
        selected=overall_score >= self.cutoff_score

        reasoning="Candidate evaluated based on explicit resume content using semantic similarity and clear numeric scoring"

        strengths=[skill for skill, score in skills_scores.items() if score > 7]
        improvement_areas=missing_skills if not selected else []

        self.resume_strengths=strengths

        return {
            "overall_score": overall_score,
            "skills_scores": skills_scores,
            "skill_reasoning": skill_reasoning,
            "selected": selected,
            "reasoning": reasoning,
            "missing_skills": missing_skills,
            "improvement_areas": improvement_areas
        }
    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        """Analyze the resume against role requirements or a custom job description."""
        try:
            # Extract text from resume
            print("Extracting text from resume...")
            self.resume_text = self.extract_text_from_file(resume_file)
            
            if not self.resume_text or len(self.resume_text.strip()) < 50:
                print("Error: Resume text is too short or empty")
                return None
            
            print(f"Resume text extracted: {len(self.resume_text)} characters")

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as tmp:
                tmp.write(self.resume_text)
                self.resume_file_path = tmp.name
            
            # Create vector store (optional)
            self.rag_vectorstore = self.create_rag_vector_store(self.resume_text)

            # Extract skills and analyze
            if custom_jd:
                print("Extracting skills from job description...")
                self.jd_text = self.extract_text_from_file(custom_jd)
                if not self.jd_text:
                    print("Error: Could not extract text from job description")
                    return None
                self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
            elif role_requirements:
                print("Using provided role requirements...")
                self.extracted_skills = role_requirements
            else:
                print("Error: No skills or job description provided")
                return None
            
            if not self.extracted_skills:
                print("Error: No skills extracted")
                return None
                
            print(f"Skills to analyze: {self.extracted_skills}")
            
            # Perform skill analysis
            print("Starting skill analysis...")
            self.analysis_result = self.semantic_skill_analysis(self.resume_text, self.extracted_skills)
            
            if not self.analysis_result:
                print("Error: Skill analysis failed")
                return None
            
            print("Skill analysis completed successfully")
            
            # Analyze weaknesses if needed
            if self.analysis_result and "missing_skills" in self.analysis_result and self.analysis_result["missing_skills"]:
                print("Analyzing weaknesses...")
                self.analyze_resume_weaknesses()
                self.analysis_result["detailed_weaknesses"] = self.resume_weaknesses
            
            return self.analysis_result
            
        except Exception as e:
            print(f"Error in analyze_resume: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def ask_question(self, question):
        """Ask a question about the resume using the RAG vector store or direct analysis."""
        if not self.resume_text:
            return "Please analyze a resume first."
        
        # If vector store is available, use it
        if self.rag_vectorstore and LANGCHAIN_AVAILABLE:
            try:
                retriever = self.rag_vectorstore.as_retriever(search_kwargs={"k":3})
                qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm_client if GROQ_AVAILABLE else ChatGroq(model="openai/gpt-oss-120b", api_key=self.groq_api_key, temperature=0),
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=False
                )
                response = qa_chain.run(question)
                return response
            except Exception as e:
                print(f"Error using vector store: {e}")
                # Fall back to direct analysis
        
        # Direct analysis fallback
        try:
            prompt = f"""
            Based on the following resume content, please answer this question: {question}
            
            Resume Content:
            {self.resume_text}
            
            Provide a detailed and accurate answer based only on the information available in the resume.
            """
            
            response = self.llm_client.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error analyzing resume: {e}"

    def generate_interview_questions(self, num_questions=5, difficulty="medium", question_types=None):
        """Generate interview questions based on the resume content."""
        if not self.resume_text or not self.extracted_skills:
            return []
        
        if question_types is None:
            question_types = ["technical", "behavioral", "situational"]
            
        try:
            context = f"""
Resume Content:
{self.resume_text[:2000]}...
Skills to focus on: {', '.join(self.extracted_skills[:10])}
Strengths: {', '.join(self.resume_strengths[:5])}
Areas for improvement: {', '.join(self.analysis_result.get('missing_skills', [])[:5])}
            """

            prompt = f"""
Generate {num_questions} personalized {difficulty.lower()} level interview questions for a candidate based on their resume content and skills. Include only the following question types: {', '.join(question_types)}.

For each question:
1. Clearly label the question type.
2. Make the question specific to their background and skills.
3. For coding questions, include a clear problem statement.

{context}

Format your response as a JSON array of objects with the following structure:
[
    {{
        "type": "question_type",
        "question": "The actual question",
        "focus_area": "skill or area being tested"
    }}
]

Return only valid JSON, no other text.
            """

            response = self.llm_client.invoke(prompt)
            try:
                questions = json.loads(response.content)
                return questions
            except json.JSONDecodeError:
                # Fallback to basic questions if JSON parsing fails
                return [
                    {
                        "type": "technical",
                        "question": f"Can you explain your experience with {self.extracted_skills[0] if self.extracted_skills else 'your main technical skill'}?",
                        "focus_area": self.extracted_skills[0] if self.extracted_skills else "general"
                    }
                ]
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return []
    
    def generate_improved_resume(self, industry="Technology/Software", experience_level="Mid Level", resume_format="Modern Professional", enhancement_options=None):
        """Generate an improved version of the resume based on analysis and preferences."""
        if not self.resume_text or not self.analysis_result:
            return None
        
        if enhancement_options is None:
            enhancement_options = ["ATS Keyword Optimization", "Action Verb Enhancement"]
        
        try:
            print("Generating improved resume...")
            
            # Create enhancement context
            context = f"""
Original Resume:
{self.resume_text}

Analysis Results:
- Overall Score: {self.analysis_result.get('overall_score', 0)}%
- Missing Skills: {', '.join(self.analysis_result.get('missing_skills', []))}
- Strengths: {', '.join(self.resume_strengths)}

Target Industry: {industry}
Experience Level: {experience_level}
Desired Format: {resume_format}
Enhancement Options: {', '.join(enhancement_options)}
            """
            
            prompt = f"""
You are a professional resume writer and career coach. Based on the provided resume analysis and requirements, create an improved version of the resume.

{context}

Requirements:
1. Maintain all factual information from the original resume
2. Enhance language and presentation based on the selected options
3. Optimize for the target industry: {industry}
4. Format appropriately for {experience_level}
5. Apply the following enhancements: {', '.join(enhancement_options)}

Please provide:
1. The complete improved resume content
2. A list of specific improvements made
3. ATS optimization analysis

Format your response as JSON:
{{
    "content": "The complete improved resume text",
    "improvements": ["List of specific improvements made"],
    "ats_analysis": {{
        "score": 85,
        "improvement": 15,
        "keywords_matched": 12,
        "keywords_added": 5,
        "readability": 8,
        "recommendations": ["ATS recommendation 1", "ATS recommendation 2"]
    }}
}}

Return only valid JSON, no other text.
            """
            
            response = self.llm_client.invoke(prompt)
            
            try:
                improved_resume = json.loads(response.content)
                print("Improved resume generated successfully")
                return improved_resume
            except json.JSONDecodeError:
                print("Failed to parse JSON response, creating fallback response")
                # Fallback response if JSON parsing fails
                return {
                    "content": response.content,
                    "improvements": [
                        "Enhanced professional language",
                        "Improved formatting and structure",
                        "Added industry-specific keywords"
                    ],
                    "ats_analysis": {
                        "score": 80,
                        "improvement": 10,
                        "keywords_matched": 8,
                        "keywords_added": 3,
                        "readability": 7,
                        "recommendations": [
                            "Consider adding more quantified achievements",
                            "Include additional industry-specific keywords"
                        ]
                    }
                }
        
        except Exception as e:
            print(f"Error generating improved resume: {e}")
            return None
    
    def convert_to_markdown(self, resume_content):
        """Convert resume content to markdown format."""
        try:
            prompt = f"""
Convert the following resume content to well-formatted Markdown:

{resume_content}

Use proper Markdown formatting:
- # for main sections
- ## for subsections  
- **bold** for emphasis
- - for bullet points
- Proper spacing and structure

Return only the Markdown content, no other text.
            """
            
            response = self.llm_client.invoke(prompt)
            return response.content
            
        except Exception as e:
            print(f"Error converting to markdown: {e}")
            # Fallback: basic markdown conversion
            lines = resume_content.split('\n')
            markdown_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    markdown_lines.append('')
                elif line.isupper() and len(line) > 3:
                    # Likely a section header
                    markdown_lines.append(f'## {line.title()}')
                elif line.endswith(':') and len(line.split()) <= 3:
                    # Likely a subsection
                    markdown_lines.append(f'### {line}')
                elif line.startswith('•') or line.startswith('-'):
                    # Bullet point
                    markdown_lines.append(f'- {line[1:].strip()}')
                else:
                    markdown_lines.append(line)
            
            return '\n'.join(markdown_lines)
    
    def analyze_ats_compatibility(self, resume_content, target_keywords=None):
        """Analyze resume for ATS compatibility."""
        if target_keywords is None:
            target_keywords = self.extracted_skills or []
        
        try:
            prompt = f"""
Analyze the following resume for ATS (Applicant Tracking System) compatibility:

Resume Content:
{resume_content}

Target Keywords: {', '.join(target_keywords)}

Provide analysis on:
1. Keyword density and matching
2. Format compatibility
3. Readability score
4. Specific recommendations for improvement

Format as JSON:
{{
    "score": 85,
    "keywords_found": ["keyword1", "keyword2"],
    "keywords_missing": ["keyword3", "keyword4"],
    "format_issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"]
}}

Return only valid JSON.
            """
            
            response = self.llm_client.invoke(prompt)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback analysis
                keywords_found = [kw for kw in target_keywords if kw.lower() in resume_content.lower()]
                keywords_missing = [kw for kw in target_keywords if kw.lower() not in resume_content.lower()]
                
                return {
                    "score": min(85, int((len(keywords_found) / max(len(target_keywords), 1)) * 100)),
                    "keywords_found": keywords_found,
                    "keywords_missing": keywords_missing,
                    "format_issues": [],
                    "recommendations": [
                        f"Add missing keywords: {', '.join(keywords_missing[:3])}",
                        "Use standard section headers",
                        "Quantify achievements with numbers"
                    ]
                }
        
        except Exception as e:
            print(f"Error analyzing ATS compatibility: {e}")
            return {
                "score": 70,
                "keywords_found": [],
                "keywords_missing": target_keywords,
                "format_issues": ["Unable to analyze"],
                "recommendations": ["Please try again"]
            }
    
    def get_industry_keywords(self, industry):
        """Get industry-specific keywords for optimization."""
        industry_keywords = {
            "Technology/Software": [
                "software development", "programming", "coding", "debugging", "testing",
                "agile", "scrum", "DevOps", "cloud computing", "API", "database",
                "full-stack", "frontend", "backend", "mobile development"
            ],
            "Healthcare/Medical": [
                "patient care", "medical records", "HIPAA", "clinical", "diagnosis",
                "treatment", "healthcare", "medical", "nursing", "pharmacy",
                "EMR", "EHR", "medical terminology", "patient safety"
            ],
            "Finance/Banking": [
                "financial analysis", "risk management", "compliance", "audit",
                "investment", "portfolio", "banking", "credit", "loans",
                "financial modeling", "budgeting", "forecasting", "regulatory"
            ],
            "Marketing/Sales": [
                "digital marketing", "SEO", "SEM", "social media", "content marketing",
                "lead generation", "sales funnel", "CRM", "campaign management",
                "brand management", "market research", "analytics", "conversion"
            ],
            "Engineering": [
                "design", "manufacturing", "quality control", "project management",
                "CAD", "technical drawings", "specifications", "testing",
                "process improvement", "safety", "compliance", "maintenance"
            ]
        }
        
        return industry_keywords.get(industry, [])
    
    def enhance_with_action_verbs(self, text):
        """Replace weak verbs with strong action verbs."""
        action_verb_replacements = {
            "did": "executed",
            "made": "created",
            "helped": "assisted",
            "worked on": "developed",
            "was responsible for": "managed",
            "handled": "coordinated",
            "dealt with": "resolved",
            "used": "utilized",
            "got": "achieved",
            "did work": "performed"
        }
        
        enhanced_text = text
        for weak_verb, strong_verb in action_verb_replacements.items():
            enhanced_text = enhanced_text.replace(weak_verb, strong_verb)
        
        return enhanced_text
    
    def quantify_achievements(self, text):
        """Add suggestions for quantifying achievements."""
        try:
            prompt = f"""
Analyze the following resume text and suggest specific ways to quantify achievements with numbers, percentages, or metrics:

{text}

For each suggestion, provide:
1. The original statement
2. A quantified version with realistic placeholder numbers
3. The type of metric used

Format as JSON:
{{
    "suggestions": [
        {{
            "original": "Improved team productivity",
            "quantified": "Improved team productivity by 25% through process optimization",
            "metric_type": "percentage"
        }}
    ]
}}

Return only valid JSON.
            """
            
            response = self.llm_client.invoke(prompt)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "suggestions": [
                        {
                            "original": "Generic achievement statement",
                            "quantified": "Add specific numbers, percentages, or timeframes",
                            "metric_type": "various"
                        }
                    ]
                }
        
        except Exception as e:
            print(f"Error quantifying achievements: {e}")
            return {"suggestions": []}