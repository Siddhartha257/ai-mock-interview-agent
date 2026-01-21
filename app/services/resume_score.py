from sentence_transformers import SentenceTransformer
import numpy as np
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import os
from models.schema import ScoreFormat

load_dotenv()

# Defining Model
llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.3,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    api_key=os.environ["GROQ_API_KEY"]
)


structured_llm = llm.with_structured_output(ScoreFormat)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Helper Funtions 
def profile_to_text(profile):
    parts = []

    # Using dot notation for Pydantic attributes
    parts.append(profile.summary)

    # projects titles + descriptions
    for p in profile.projects:
        parts.append(p.title)
        # Assuming description is a list of strings
        parts.extend(p.description)

    # work experience
    for w in profile.work_experience:
        parts.append(w.company)
        parts.append(w.duration)
        parts.extend(w.description)

    return ' '.join(parts)

def list_to_text(lis):
    return ' '.join(x for x in lis)

# Finds the similarity between embeddings
def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# converts text into vectors
def embed(text:str):
    text_encode = model.encode(text, normalize_embeddings=True).tolist()
    return text_encode

# Calculates the similarity score between user profile and job profile and returns the score
def similarity_score(user_profile , job_profile):
    user_profile_text = profile_to_text(user_profile)
    user_profile_embedd = embed(user_profile_text)
    job_profile_embedd = embed(job_profile)

    score = cosine_sim(user_profile_embedd , job_profile_embedd)
    return score

# finds the matched skills between user and jd
def get_matched_skills(job_skills, user_skills):
    prompt = f"""
    Act as an ATS system. Compare User Skills against Job Skills.
    Rules:
    1. Handle synonyms (e.g., 'AI' matches 'Artificial Intelligence').
    2. Assign importance (weight 1-5) to each Job Skill.
    3. Calculate the final_score as: (Sum of weights of matched skills) / (Total sum of all job skill weights).
    Job Skills: {", ".join(job_skills)}
    User Skills: {", ".join(user_skills)}
    """
    
    try:
        # The output is already a ScoreFormat object
        result = structured_llm.invoke(prompt)
        
        # You can access attributes directly: result.final_score, result.matches
        return result.final_score
    except Exception as e:
        print(f"Error during structured output: {e}")
        return 0.0

# returns the final resume score 

def get_resume_score(user_profile, job_profile_text, user_skills, job_skills):
    # Calculate Embedding Similarity (Context)
    sim = similarity_score(user_profile, job_profile_text)
    
    # Calculate Structured Skill Match (Technical)
    skills_score = get_matched_skills(job_skills, user_skills)

    # Hybrid Score: 40% Context, 60% Skills
    final_score = (sim * 0.4) + (skills_score * 0.6)
    return round(final_score, 4)
