import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

# Defining Model


model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.environ["GOOGLE_API_KEY"],
)
def resume_enhancer(user_profile, job_profile):
    prompt = (
        "Role: Expert Career Coach & ATS Optimizer. "
        "Task: Tailor the user's resume to the job profile using ONLY provided facts. "
        "Strict Rule: If there is no significant skill overlap, return 'this is irrelevant job'.\n\n"

        "Requirements:\n"
        "1. Professional Summary: Exactly one high-impact sentence.\n"
        "2. Keyword Optimization: Map user skills to job-specific terminology.\n"
        "3. Impact: Use action verbs and include [quantifiable metrics] where possible.\n"
        "4. Structure: Markdown format with sections: Summary, Technical Skills, Experience, and Projects.\n"
        "5. Constraint: Zero hallucination. Do not invent roles or technologies.\n\n"

        f"User Data: {user_profile}\n"
        f"Job Data: {job_profile}\n\n"
        "Output Markdown only. No preamble, No Headers , No footers ."
    )

    output = model.invoke(prompt)
    return output.content


def get_enhanced_resume(user_profile, job_profile):
    try:
        # 1. Generate Content
        content = resume_enhancer(user_profile, job_profile)

        # 2. Early Exit for Irrelevant Jobs
        if "irrelevant job" in content.lower():
            return "Resume generation cancelled: Job profile does not match user skills."

        # 3. Path Setup
        directory = "resources"
        file_path = os.path.join(directory, "enhanced_resume.md")

        # 4. Handle Directory Creation Errors
        try:
            os.makedirs(directory, exist_ok=True)
        except PermissionError:
            return f"Error: No permission to create directory {directory}."

        # 5. Atomic-style Write (Handle Write/System Errors)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Success: Resume saved at {file_path}"

    except IOError as e:
        # Handles disk full, file locks, or hardware failure
        return f"File System Error: Could not write file. {e}"
    except Exception as e:
        # Catches unexpected logic or API errors
        return f"An unexpected error occurred: {e}"
