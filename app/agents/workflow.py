from typing import List
from langgraph.graph import StateGraph,START , END
from pydantic import BaseModel
from typing import Optional, Annotated
import operator


from models.schema import Profile, JDFormat
from services.resume_parser import get_user_profile
from services.jd_parser import get_job_profile
from services.resume_score import get_resume_score
from services.resume_enhancer import get_enhanced_resume
from services.questions_generator import generate_question
from services.topics_generator import generate_topics
from models.schema import Chat , EvaluateFormat
from services.evaluator import evaluate
from langgraph.checkpoint.memory import MemorySaver


checkpoint = MemorySaver()

class State(BaseModel):
    resume_path: str
    jd_path: str
    user_profile: Optional[Profile] = None
    job_profile: Optional[JDFormat] = None
    resume_score: float = 0.0
    enhanced_resume_path: Optional[str] = None
    topics: List[str] = []
    current_topic_index: int = 0
    question_count: int = 0
    last_question: str = ""
    chats: Annotated[List[Chat], operator.add] = []
    result: Optional[EvaluateFormat] = None

def inputs(state: State):
    u_profile = get_user_profile(state.resume_path)
    j_profile = get_job_profile(state.jd_path)
    return {"user_profile": u_profile, "job_profile": j_profile}

def resume_screening(state: State):
    return{'resume_score':get_resume_score(state.user_profile ,state.job_profile.summary ,state.user_profile.skills,state.job_profile.skills)}

def interview_condition(state: State):
    if state.resume_score >=0.4:
        return True
    else:
        return False


def topics_node(state: State):
    # 1. Call your service
    result = generate_topics(state.user_profile, state.job_profile)

    # 2. Extract ONLY the list of strings
    # If generate_topics returns a TopicsFormat object, use result.topics
    # If it returns a dict, use result['topics']
    if hasattr(result, 'topics'):
        topics_list = result.topics
    elif isinstance(result, dict) and 'topics' in result:
        topics_list = result['topics']
    else:
        topics_list = result  # Assume it's already the list

    # 3. Return it clearly
    return {'topics': topics_list}


def question_node(state: State):
    # Ensure question_count is not None
    current_count = state.question_count if state.question_count is not None else 0
    
    # Call your service
    result = generate_question(
        state.topics,
        state.current_topic_index,
        state.chats,
        current_count
    )

    # Handle the response from generate_question
    # It returns: {"last_question": str, "question_count": int}
    if isinstance(result, dict):
        if 'last_question' in result:
            q_text = result['last_question']
        elif 'question' in result:
            q_text = result['question']
        elif 'output' in result:
            q_text = result['output']
        else:
            q_text = str(result)
    elif hasattr(result, 'last_question'):
        q_text = result.last_question
    elif hasattr(result, 'question'):
        q_text = result.question
    elif hasattr(result, 'output'):
        q_text = result.output
    else:
        # Fallback if result is just the string itself
        q_text = str(result)

    return {
        "last_question": q_text,
        "question_count": current_count + 1
    }

def interview_router(state: State):
    current_count = state.question_count if state.question_count is not None else 0
    if current_count >= 2:
        # Stop looping if we've hit the end of the topics list
        current_index = state.current_topic_index if state.current_topic_index is not None else 0
        if current_index >= len(state.topics) - 1:
            return "finish"
        return "next_topic"
    return "ask_again"




def resume_enhancements(state: State):
    return {'enhanced_resume_path': get_enhanced_resume(state.user_profile , state.job_profile)}

def final_evaluation(state: State):
    return {'result':evaluate(state.chats)}

agent = StateGraph(State)

agent.add_node('inputs',inputs)
agent.add_node('resume_screening',resume_screening)
agent.add_node('interview_condition',interview_condition)
agent.add_node('topics_node',topics_node)
agent.add_node('resume_enhancements',resume_enhancements)
agent.add_node('question_node',question_node)
agent.add_node('final_evaluation',final_evaluation)

agent.add_edge(START , 'inputs')
agent.add_edge('inputs','resume_screening')
agent.add_conditional_edges('resume_screening',interview_condition,{True:'topics_node',False:'resume_enhancements'})
agent.add_edge('topics_node','question_node')

agent.add_conditional_edges(
    'question_node',
    interview_router,
    {
        "ask_again": "question_node",
        "next_topic": "question_node",
        "finish": "final_evaluation"
    }
)

agent.add_edge('resume_enhancements', END)
agent.add_edge('final_evaluation', END)

interview = agent.compile(checkpointer=checkpoint, interrupt_after=["resume_screening","question_node"])