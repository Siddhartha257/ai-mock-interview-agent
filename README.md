# 🤖 AI Interview Agent

An end-to-end intelligent interview assistant that automates candidate screening, conducts conversational interviews, and provides personalized feedback.

## 🎯 Overview

This project delivers a complete AI-powered interview platform that:

- ✅ Reads resumes and job descriptions
- ✅ Screens candidate fit automatically
- ✅ Conducts adaptive conversational interviews
- ✅ Evaluates answers in real-time
- ✅ Generates final scores with feedback
- ✅ Suggests personalized resume improvements
- ✅ Uses company knowledge (RAG) for context-aware questions

---

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐
│  Resume Parser  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Resume Screening│◄─────┤ Job Description  │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Interview Loop │◄─────┤  Knowledge Base  │
└────────┬────────┘      │      (RAG)       │
         │               └──────────────────┘
         ▼
┌─────────────────┐
│ Final Scoring & │
│   Enhancement   │
└─────────────────┘
```

---

## 📦 Features

### 1. Resume & Job Parsing

**Purpose:** Extract structured information from candidate resumes and job descriptions.

**Outputs:**
- Candidate skills
- Project summaries
- Domain keywords
- Job role and requirements
- Missing skills gap analysis

**Tools:**
- LLM-based extraction
- PDF/Word parsers

### 2. Resume Screening

**Purpose:** Automatically evaluate candidate-job fit.

**Metrics:**
- Skill overlap percentage
- Missing critical items
- Weighted compatibility score
- Pass/fail threshold

**Flow:**
- Low score → Skip interview → Provide enhancement suggestions
- Acceptable score → Proceed to interview

### 3. Conversational Interview Loop

**Purpose:** Conduct an adaptive, intelligent interview conversation.

**Capabilities:**
- Asks one question at a time
- Waits for user response
- Evaluates answer quality
- Dynamically generates follow-up questions
- Adjusts difficulty based on performance
- Early termination for excellent/weak candidates

**Implementation:**
Uses LangGraph pause/resume pattern for stateful conversations.

### 4. Question Generation

**Context-aware questions based on:**
- Job requirements
- Candidate's projects and experience
- Identified skill gaps
- Retrieved company knowledge
- Previous answer quality

**Example Prompts:**
```
"Ask a medium difficulty question about {skill}"
"Ask a follow-up to clarify the candidate's understanding of {concept}"
```

### 5. Answer Evaluation

**Scoring criteria:**
- Technical correctness
- Clarity of explanation
- Relevance to job requirements
- Alignment with company expectations

**Tracking:**
- Per-answer scores
- Running average
- Weakness pattern detection

**Modes:**
- Real-time (per answer)
- Batch (after completion)

### 6. Final Scoring

**Computed from:**
- Resume match score
- Interview answer scores
- Performance consistency
- Difficulty progression

**Output format:**
```json
{
  "score": 85,
  "rating": "Strong",
  "summary": "Candidate demonstrates solid understanding..."
}
```

### 7. Resume Enhancement Suggestions

**Triggered when:**
- Resume match score is low, OR
- Interview performance is below threshold
