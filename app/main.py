import os
import uuid
import tempfile
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Import your compiled interview graph
from agents.workflow import interview
from models.schema import Chat

app = FastAPI(title="AI Interview Backend - File Uploads")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProceedRequest(BaseModel):
    thread_id: str


class AnswerRequest(BaseModel):
    thread_id: str
    answer: str


# --- Endpoints ---

@app.post("/start-interview")
async def start_interview(
        resume: UploadFile = File(...),
        jd: UploadFile = File(...)
):
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    # Create temporary files to store the uploaded content
    # These will be deleted after the 'finally' block
    temp_resume = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_jd = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    try:
        # 1. Save uploaded content to temp files
        shutil.copyfileobj(resume.file, temp_resume)
        shutil.copyfileobj(jd.file, temp_jd)

        # Close files to ensure they are written to disk
        temp_resume.close()
        temp_jd.close()

        initial_input = {
            "resume_path": temp_resume.name,
            "jd_path": temp_jd.name
        }

        # 2. Run 'inputs' -> 'resume_screening' -> PAUSE
        for event in interview.stream(initial_input, config, stream_mode="updates"):
            print(f"Node Executed: {list(event.keys())[0]}")

        snapshot = interview.get_state(config)
        resume_score = snapshot.values.get("resume_score", 0.0)

        return {
            "status": "screening_complete",
            "thread_id": session_id,
            "resume_score": resume_score,
            "can_proceed": resume_score >= 0.4
        }

    except Exception as e:
        print(f"Start Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 3. CLEANUP: Remove the temporary files from the server
        if os.path.exists(temp_resume.name):
            os.remove(temp_resume.name)
        if os.path.exists(temp_jd.name):
            os.remove(temp_jd.name)


@app.post("/proceed-to-interview")
async def proceed(payload: ProceedRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    snapshot = interview.get_state(config)

    if not snapshot.next:
        raise HTTPException(status_code=400, detail="Session not found or finished.")

    try:
        for event in interview.stream(None, config, stream_mode="updates"):
            print(f"Node Executed: {list(event.keys())[0]}")

        new_snapshot = interview.get_state(config)

        if not new_snapshot.next:
            return {
                "status": "failed_screening",
                "enhanced_resume_path": new_snapshot.values.get("enhanced_resume_path")
            }

        return {
            "status": "interview_started",
            "first_question": new_snapshot.values.get("last_question"),
            "topics": new_snapshot.values.get("topics")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit-answer")
async def submit_answer(payload: AnswerRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    snapshot = interview.get_state(config)

    if not snapshot.next:
        raise HTTPException(status_code=400, detail="Interview session ended.")

    try:
        vals = snapshot.values
        new_chat = Chat(question=vals.get("last_question"), answer=payload.answer)

        # Topic Logic
        update_data = {"chats": [new_chat]}
        question_count = vals.get("question_count") or 0
        current_topic_index = vals.get("current_topic_index") or 0
        topics = vals.get("topics") or []
        
        if question_count >= 2:
            if current_topic_index + 1 < len(topics):
                update_data["current_topic_index"] = current_topic_index + 1
                update_data["question_count"] = 0

        interview.update_state(config, update_data)

        for event in interview.stream(None, config, stream_mode="updates"):
            pass

        new_snapshot = interview.get_state(config)

        if not new_snapshot.next:
            return {"status": "completed", "final_result": new_snapshot.values.get("result")}

        # Get current topic safely
        response_topics = new_snapshot.values.get("topics") or []
        response_topic_index = new_snapshot.values.get("current_topic_index") or 0
        current_topic = response_topics[response_topic_index] if response_topics else "General"
        
        return {
            "status": "ongoing",
            "next_question": new_snapshot.values.get("last_question"),
            "topic": current_topic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-enhanced-resume")
async def get_enhanced_resume():
    """Return the enhanced resume content as markdown"""
    file_path = os.path.join("resources", "enhanced_resume.md")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Enhanced resume not found. Please complete the screening first.")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content,
            "filename": "enhanced_resume.md"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)