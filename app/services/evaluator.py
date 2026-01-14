from langchain_groq import ChatGroq
from models.schema import EvaluateFormat , Chat
from dotenv import load_dotenv
import os
from typing import List


load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.3,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    api_key=os.environ["GROQ_API_KEY"]
)



def evaluate(all_chats: List[Chat]):
    structured_llm = llm.with_structured_output(EvaluateFormat)

    transcript = ""
    for i, chat in enumerate(all_chats, start=1):
        transcript += f"Q{i}: {chat.question}\n"
        transcript += f"A{i}: {chat.answer}\n\n"

    prompt = (
        "You are an expert technical interviewer and evaluation specialist.\n"
        "Evaluate this interview transcript ONLY based on the candidate answers.\n\n"
        "Required output:\n"
        "- topic_scores: cluster questions into meaningful topics (ex: ML, APIs, DB) and rate 1-5\n"
        "- strengths: 3-5 positive observations\n"
        "- weaknesses: 3-5 growth areas\n"
        "- final_score: overall score (1 = weak, 5 = excellent)\n"
        "- recommendation: 'hire', 'maybe', 'no-hire'\n"
        "- summary: 3-5 sentence overview\n\n"
        "Return a response strictly matching the EvaluateFormat schema.\n\n"
        "Transcript:\n"
        f"{transcript}"
    )
    result = structured_llm.invoke(prompt)
    return result
