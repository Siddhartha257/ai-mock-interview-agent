import os
from dotenv import load_dotenv
from models.schema import TopicsFormat
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def generate_topics(user_profile, job_profile):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    structured_llm = llm.with_structured_output(TopicsFormat)
    prompt = (
        "You are a senior technical interviewer.\n"
        "From the following structured details, extract EXACTLY 4 relevant "
        "technical interview topics.\n"
        f"User Summary: {user_profile.summary}\n"
        f"User Skills: {', '.join(user_profile.skills)}\n"
        f"Job Summary: {job_profile.summary}\n"
        f"Job Skills: {', '.join(job_profile.skills)}"
    )

    output = structured_llm.invoke(prompt)
    return output