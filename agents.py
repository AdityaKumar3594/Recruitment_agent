import re 
import PyPDF2
import io
from langchain import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os 
import json

class ResumeAnalysisAgent:
    def __init__(self, api_key, cutoff_score=75):
        self.api_key=api_key
        self.cutoff_score=cutoff_score
        self.resume_text = None
        self.rag_vectorstore = None
        self.analysis_result = None
        self.jd_text = None
        self.extracted_skills = None
        self.resume_weaknesses = []
        self.resume_strengths = []
        self.improvement_suggestions = {}

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
        try:
            text_splitter = RecursiveCharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len,)
            chunks = text_splitter.split_text(text)
            embeddings = OpenAIEmbeddings(api_key=self.api_key)
            vectorstore = FAISS.from_texts(chunks, embeddings)
            return vectorstore
    
    def create_vector_store(self,text):
        """Create a vector store from the provided text."""
        embeddings = OpenAIEmbeddings(api_key=self.api_key)
        vectorstore = FAISS.from_texts(chunks, embeddings)
        return vectorstore
    
    def analyze_skill(self, qa_chain, skill):
        """Analyze a specific skill using the QA chain."""
        query = f"Does the resume mention the skill '{skill}'? Provide numeric rating on a scale of 0-10 ,followed by reasoning."
        result = qa_chain.run(query)
        match = re.search(r"(\d{1,2})", result)
        score = int(match.group(1)) if match else 0

        reasoning = result.split('.', 1)[1].strip() if '.' in result and len(result.split('.', 1)) > 1 else "No reasoning provided."
        return skill, min(score, 10), reasoning
    def analyze_resume_weaknesses(self):
        """Analyze the resume for weaknesses based on the job description."""
        if not self.resume_text or not self.extracted_skills or not self.analysis_result:
            return []
        weaknesses = []
        for skill in self.analysis_result.get('missing_skills', []):
            llm=ChatOpenAI(model="gpt-4o",api_key=self.api_key,temperature=0)
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
            response = llm.invoke(prompt)
            try:
                weakness_data = json.loads(weakness_content)
                weakness_detail={
                    "skill":skill,
                    "score":self.analysis_result['skills_scores'].get(skill, 0),
                    "detail": weakness_data.get("weakness", "No specific details provided."),
                    "suggestions": weakness_data.get("improvement_suggestions", []),
                    "example": weakness_data.get("example", "No specific example provided")
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
                    "detail":weakness_content[:200]
                })
        self.resume_weaknesses = weaknesses
        return weaknesses
    def extract_skills_from_jd(self, jd_text):
        """Extract skills from the job description text."""
        try:
            llm = ChatOpenAI(model="gpt-4o", api_key=self.api_key)
            prompt = f"""Extract a comprehensive list of technical skills,technology,and
            competencies from the following job description.
            Format the output as a Python list of strings.Only include the list,nothing else.
            Job Description: {jd_text}
            """
            response=llm.invoke(prompt)
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
                    line = line[2:].strip()
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
        retriever = vectorstore.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o", api_key=self.api_key, temperature=0),
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
    def analyze_resume(self,resume_file,role_requirements=None,custom_jd=None):
        """Analyze the resume against role requirements or a custom job description."""
        self.resume_text=self.extract_text_from_file(resume_file)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt",mode='w',encoding='utf-8') as tmp:
            tmp.write(self.resume_text)
            self.resume_file_path=tmp.name
        self.rag_vectorstore=self.create_rag_vector_store(self.resume_text)

        if custom_jd:
            self.jd_text=self.extract_text_from_file(custom_jd)
            self.extracted_skills=self.extract_skills_from_jd(self.jd_text)
            self.analysis_result=self.semantic_skill_analysis(self.resume_text,self.extracted_skills)
        elif role_requirements:
            self.extracted_skills=role_requirements
            self.analysis_result=self.semantic_skill_analysis(self.resume_text,role_requirements)
        
        if self.analysis_result and "misssing_skills" in self.analysis_result and self.analysis_result["missing_skills"]:
            self.analyze_resume_weaknesses()

            self .analysis_result["detailed_weaknesses"]=self.resume_weaknesses
        
        return self.analysis_result
    
    def ask_question(self, question):
        """Ask a question about the resume using the RAG vector store."""
        if not self.rag_vectorstore or not self.resume_text:
            print("RAG vector store not initialized. Please analyze a resume first.")
            return ""
        retriever = self.rag_vectorstore.as_retriever(search_kwarsgs={"k":3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4o", api_key=self.api_key, temperature=0),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False
        )
        response = qa_chain.run(question)
        return response

    def generate_interview_questions(self, num_questions=5):
        """Generate interview questions based on the resume content."""
        if not self.resume_text:
            print("Resume text not available. Please analyze a resume first.")
            return []
        llm = ChatOpenAI(model="gpt-4o", api_key=self.api_key, temperature=0)
        prompt = f"""
        Based on the following resume content, generate a list of {num_questions} relevant interview questions that assess the candidate's skills and experiences.
        Resume Content: {self.resume_text[:3000]}...
        Provide the questions as a numbered list.
        """
        response = llm.invoke(prompt)
        questions = []
        for line in response.content.split('\n'):
            line = line.strip()
            if re.match(r'^\d+\.', line):
                question = re.sub(r'^\d+\.\s*', '', line)
                questions.append(question)
        return questions
    


    



        



  

           


    

                        


        


        
  

