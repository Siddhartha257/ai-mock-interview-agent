import os
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def generate_question(topics, current_topic_index, chats, question_count):
    topic = topics[current_topic_index]

    # Format the last few exchanges for LLM context
    history_str = ""
    if chats:
        # Take the last 2 interactions for context
        recent_chats = chats[-2:]
        history_str = "\n".join([f"Q: {c.question}\nA: {c.answer}" for c in recent_chats])

    ask_prompt = (
        "You are a technical interviewer.\n"
        f"Topic: {topic}\n"
        f"History:\n{history_str}\n\n"
        "Ask ONE new question about this topic only. "
        "Before asking, give a small natural reaction on the previous answer if history exists."
    )

    question = llm.invoke(ask_prompt).content.strip()

    return {
        "last_question": question,
        "question_count": question_count + 1
    }