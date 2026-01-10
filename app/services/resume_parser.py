from langchain_unstructured import UnstructuredLoader
from models.schema import Profile
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0.5,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    api_key=os.environ["GROQ_API_KEY"]
)

structured_llm = llm.with_structured_output(Profile)


def load_document(file_path):
    loader = UnstructuredLoader(file_path)
    docs = loader.load()
    resume_text = "\n".join(doc.page_content for doc in docs)
    return resume_text


def get_user_profile(file_path: str) -> Profile:
    resume_text = load_document(file_path)

    prompt = f"""
    Extract the candidate profile from this resume text.
    Return JSON that matches the Profile schema.
    Resume:
    {resume_text}
    """

    result: Profile = structured_llm.invoke(prompt)
    return result


if __name__ == "__main__":
    data = get_user_profile("app/resources/siddu's resume.pdf")
    print(data.model_dump())
