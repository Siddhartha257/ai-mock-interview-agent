from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def profile_to_text(profile):
    parts = []

    parts.append(profile['summary'])

    # projects titles + descriptions
    for p in profile['projects']:
        parts.append(p['title'])
        parts.extend(p['description'])

    # work experience
        # company + description
    for w in profile['work_experience']:
        parts.append(w['company'])
        parts.append(w['duration'])
        parts.extend(w['description'])

    return ' '.join(parts)

def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def embed(jd_text: str,profile_for_similarity:str):
    jd_encode = model.encode(jd_text, normalize_embeddings=True).tolist()
    profile_encode = model.encode(profile_for_similarity, normalize_embeddings=True).tolist()
    return jd_encode , profile_encode



profile = {'name': 'Sai Siddhartha Chunduru', 'gmail': 'chsiddhartha25@gmail.com', 'summary': 'AI/ML developer proficient in Python, full-stack development, and LLMs, building intelligent applications that automate processes and deliver measurable impact.', 'work_experience': [{'company': 'Coding Jr', 'duration': 'Feb 2025 – Apr 2025', 'description': ['Developed an AI Copilot using LLMs and RAG to automate common e-commerce workflows, reducing manual effort by 30% and improving operational efficiency.', 'Conducted a detailed analysis of e-Commerce processes, identifying 10+ workflow inefficiencies and designing AI-driven solutions to improve business workflows.', 'Built a search pipeline delivering faster, context-aware results, significantly reducing query resolution time and improving user experience.']}], 'projects': [{'title': 'AI-Powered Health & Fitness Tracking Platform', 'description': ['Developed a full-stack health monitoring application using Python, FastAPI, SQLAlchemy, tracking workouts, dietary intake, and providing 90% accurate nutritional data via a nutrition tracking API, reducing manual planning time by 80%.', 'Optimized database schema and implemented asynchronous processing with Pydantic, reducing API latency by 40% and ensuring reliable, continuous health monitoring.'], 'link': None}, {'title': 'SmartSlide – Automated Presentation Insights & Quiz Generator', 'description': ['Built a streamlit-based PPT analyzer in Python, supporting multi-PPT uploads, semantic search & summarization using LangChain, ChromaDB, HuggingFace embeddings, Groq LLaMA, achieving 90%+ extraction accuracy.', 'Implemented context-aware MCQ quiz generation, optimized token-aware chunking (8,000 tokens/batch), reducing API calls & memory usage by 40%, enhancing engagement & learning outcomes.'], 'link': None}], 'skills': ['Python', 'Java', 'C++', 'HTML', 'CSS', 'React.js', 'Streamlit', 'FastAPI', 'TensorFlow', 'scikit-learn', 'OpenCV', 'pandas', 'NumPy', 'Matplotlib', 'Data Structures & Algorithms', 'Object-Oriented Programming', 'Software Development', 'Machine Learning', 'AI Model Deployment', 'Jupyter Notebook', 'VS Code', 'MySQL'], 'certifications': ['FastAPI (Udemy) – Completed a comprehensive course on REST APIs, SQLAlchemy, OAuth & JWT', 'BITS Hackathon – Generative AI Track: Advanced to the final round as part of a team, developing AdVerve, an AI-powered ad copy generator.', 'Photography Club Member – Fostered teamwork while pursuing creative passion'], 'education': [{'degree': 'Bachelor of Technology in Computer Science', 'college': 'SRM AP University', 'year': '2022 – 2026', 'cgpa': '8.0/10'}]}
jd_text = """
Job Title: Machine Learning Engineer

We are looking for a Machine Learning Engineer to join our engineering team.
The candidate will build, deploy, and maintain ML models for real-world use cases.

Responsibilities:
- Develop and train models using Python, TensorFlow, PyTorch, or scikit-learn
- Collect, preprocess, and analyze structured and unstructured datasets
- Build APIs to serve ML models into production using FastAPI or Flask
- Work with cross-functional teams including data engineers and product teams
- Monitor model performance and retrain when needed

Requirements:
- Strong knowledge in Python programming
- Experience with machine learning algorithms and data analytics
- Hands-on experience with NumPy, Pandas, scikit-learn
- Understanding of deep learning frameworks like TensorFlow or PyTorch
- Familiarity with cloud platforms (AWS, GCP, Azure) is a plus
- Experience with SQL and NoSQL databases
- Good communication and problem-solving skills

Nice To Have:
- Exposure to LLMs and vector databases
- Familiarity with Docker, Git, CI/CD pipelines
"""

job_skills = ['python ', 'machine learning' , "fastapi",'AWS']

profile_for_similarity = profile_to_text(profile)
print(profile_for_similarity)
resume_vec, jd_vec = embed(jd_text , profile_for_similarity)
score = cosine_sim(resume_vec, jd_vec)
print("Similarity:", score)

