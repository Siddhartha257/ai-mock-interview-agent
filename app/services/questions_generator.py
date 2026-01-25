import os
from langchain_google_genai import ChatGoogleGenerativeAI
from models.schema import QuestionFormat

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def generate_question(topics, current_topic_index, chats, question_count):
    # Ensure question_count is not None
    safe_count = question_count if question_count is not None else 0
    safe_index = current_topic_index if current_topic_index is not None else 0
    
    structured_llm = llm.with_structured_output(QuestionFormat)
    topic = topics[safe_index]

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
        "generate the question in plain text "
    )

    question = structured_llm.invoke(ask_prompt)

    return {
        "last_question": question.output,
        "question_count": safe_count + 1
    }