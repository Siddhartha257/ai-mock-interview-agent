# 🤖 AI Mock Interview Agent

An intelligent, end-to-end interview assistant that automates resume screening, conducts adaptive conversational interviews, and provides detailed feedback to help candidates improve.

## 🎯 Overview

The AI Mock Interview Agent streamlines the recruitment and preparation process. It takes a candidate's resume and a job description, analyzes the fit, and if suitable, launches an interactive, chat-based interview tailored to the specific role.

## ✨ Features

*   **Resume & JD Parsing**: Automatically extracts skills, experience, and requirements from uploaded PDFs.
*   **Smart Screening**: Calculates a compatibility score between the candidate and the job.
    *   *Low Score (< 40%)*: Provides instant resume enhancement suggestions.
    *   *High Score (> 40%)*: Proceeds to the technical interview.
*   **Adaptive Interview Loop**:
    *   Generates relevant topics based on the JD and Resume.
    *   Asks dynamic, context-aware questions.
    *   Evaluates answers in real-time.
*   **Comprehensive Feedback**: Delivers a final evaluation report scoring technical accuracy, clarity, and relevance.

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI
*   **AI Orchestration**: LangGraph (StateGraph)
*   **Data Validation**: Pydantic
*   **ML/Embeddings**: Sentence Transformers, NumPy
*   **Frontend**: Vanilla HTML, CSS, JavaScript
*   **Chat Model** Gemini , Groq

## 🔄 Workflow

1.  **Input**: User uploads `Resume` and `Job Description`.
2.  **Analysis**: System parses documents and compiles User and Job profiles.
3.  **Decision**:
    *   **Screening**: A score is calculated.
    *   **Enhancement**: If fit is low, the workflow ends with resume improvement tips.
    *   **Interview**: If fit is high, the system generates interview topics.
4.  **Interview Session**: The agent iterates through topics, asking questions and processing user answers via a chat interface.
5.  **Completion**: The session concludes with a final performance review.


