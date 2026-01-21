import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# Import your compiled interview graph
from agents.workflow import interview
from models.schema import Chat

app = FastAPI(title="AI Interview Backend - Automated Sessions")


# --- Request Schemas ---

class StartRequest(BaseModel):
    resume_path: str
    jd_path: str


class ProceedRequest(BaseModel):
    thread_id: str


class AnswerRequest(BaseModel):
    thread_id: str
    answer: str


# --- Endpoints ---

@app.post("/start-interview")
async def start_interview(payload: StartRequest):
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    try:
        initial_input = {
            "resume_path": payload.resume_path,
            "jd_path": payload.jd_path
        }

        # Runs 'inputs' -> 'resume_screening' -> PAUSE
        for event in interview.stream(initial_input, config, stream_mode="updates"):
            print(f"Node Executed: {list(event.keys())[0]}")

        snapshot = interview.get_state(config)
        resume_score = snapshot.values.get("resume_score", 0.0)

        return {
            "status": "screening_complete",
            "thread_id": session_id,
            "resume_score": resume_score,
            "can_proceed": resume_score > 0.3  # Threshold helper for UI
        }

    except Exception as e:
        print(f"Start Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/proceed-to-interview")
async def proceed(payload: ProceedRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    snapshot = interview.get_state(config)

    # FIX: We only check IF the graph is interrupted.
    # The conditional edge in your workflow already handles the score logic.
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="Interview session is not in a state that can proceed.")

    try:
        # RESUME: Passing None tells LangGraph to continue from the last checkpoint
        # This will follow your 'interview_condition' edge automatically.
        for event in interview.stream(None, config, stream_mode="updates"):
            print(f"Node Executed: {list(event.keys())[0]}")

        new_snapshot = interview.get_state(config)

        # If the workflow went to 'resume_enhancements' and reached END
        if not new_snapshot.next:
            return {
                "status": "failed_screening",
                "message": "Resume score was too low. Enhancements generated.",
                "enhanced_resume_path": new_snapshot.values.get("enhanced_resume_path")
            }

        # If it reached 'question_node' and is now interrupted again
        return {
            "status": "interview_started",
            "first_question": new_snapshot.values.get("last_question"),
            "topics": new_snapshot.values.get("topics")
        }

    except Exception as e:
        print(f"Proceed Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit-answer")
async def submit_answer(payload: AnswerRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}
    snapshot = interview.get_state(config)

    if not snapshot.next:
        raise HTTPException(status_code=400, detail="Interview session ended.")

    try:
        vals = snapshot.values
        last_q = vals.get("last_question")
        q_count = vals.get("question_count", 0)
        curr_idx = vals.get("current_topic_index", 0)
        topics = vals.get("topics", [])

        new_chat = Chat(question=last_q, answer=payload.answer)

        # Prepare updates
        update_data = {"chats": [new_chat]}

        # Check for topic transition based on question count
        if q_count >= 2:
            if curr_idx + 1 < len(topics):
                update_data["current_topic_index"] = curr_idx + 1
                update_data["question_count"] = 0

        # Update and resume
        interview.update_state(config, update_data)

        for event in interview.stream(None, config, stream_mode="updates"):
            print(f"Node Executed: {list(event.keys())[0]}")

        new_snapshot = interview.get_state(config)

        if not new_snapshot.next:
            return {
                "status": "completed",
                "final_result": new_snapshot.values.get("result")
            }

        # Topic safety check for UI display
        try:
            current_topic = topics[new_snapshot.values.get("current_topic_index", 0)]
        except:
            current_topic = "Interview"

        return {
            "status": "ongoing",
            "next_question": new_snapshot.values.get("last_question"),
            "topic": current_topic
        }

    except Exception as e:
        print(f"Answer Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)