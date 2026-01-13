import os
from dotenv import load_dotenv
from typing import List
from models.schema import Chat , TopicsFormat
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def generate_topics(user_profile, job_profile):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
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
    return output.topics


def run_interview(user_profile, job_profile):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.5,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    topics = generate_topics(user_profile, job_profile)
    print("\nInterview Topics:", topics)

    history = ""
    all_chats = []

    for topic in topics:
        for _ in range(2):  # 1 Qs per topic
            ask_prompt = (
                "You are a technical interviewer.\n"
                f"Topic: {topic}\n"
                f"History:\n{history}\n\n"
                "Ask ONE new question about this topic only."
                "before asking the next question . give a small natural reaction on previous answer."
            )
            question = llm.invoke(ask_prompt).content.strip()
            print(f"\n{question}")
            ans = input("Answer: ").strip()

            all_chats.append(Chat(question=question, answer=ans))
            history = f"[{topic}] Q: {question}\nA: {ans}\n"
    return all_chats

if __name__ == "__main__":
    user = {
        "skills": "Python, ML, Data Analytics",
        "experience": "Built AI projects with RAG"
    }
    job = "ML Engineer with deployment experience"

    final_result = run_interview(user, job)
    print("\nFINAL RESULT STORED\n")
    print(final_result)