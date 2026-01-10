from models.schema import JDFormat
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_unstructured import UnstructuredLoader

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

structured_llm = llm.with_structured_output(JDFormat)


def load_document(file_path):
    loader = UnstructuredLoader(file_path)
    docs = loader.load()
    jd_text = "\n".join(doc.page_content for doc in docs)
    return jd_text

def get_job_profile(file_path: str) -> JDFormat:
    # Load the raw text from PDF/Docx
    jd_raw_text = load_document(file_path)

    prompt = f"""
    Analyze the following Job Description text and extract information into a structured format.
    
    Instructions:
    1. EXTRACT all technical and soft skills into the 'skills' list.
    2. SUMMARIZE the rest of the job (responsibilities, about the company, benefits) into the 'summary' field. 
    3. Ensure the 'summary' does NOT just repeat the bulleted skills list.
    
    Job Description Text:
    {jd_raw_text}
    """

    # Returns the JDFormat Pydantic object
    result: JDFormat = structured_llm.invoke(prompt)
    return result