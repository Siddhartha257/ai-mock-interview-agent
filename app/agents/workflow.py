from typing import List

from langgraph.graph import StateGraph,START , END
from pydantic import BaseModel
from models.schema import Profile,JDFormat
from services.resume_parser import get_user_profile
from services.jd_parser import get_job_profile
from services.resume_score import get_resume_score
from services.resume_enhancer import get_enhanced_resume
from services.interview import run_interview
from models.schema import Chat

class State(BaseModel):
    resume_path: str
    jd_path: str
    user_profile:Profile
    job_profile:JDFormat
    resume_score:float
    enhanced_resume_path: str
    chats : List[Chat]

def inputs(state: State):
    resume_path = state.resume_path
    jd_path = state.jd_path
    state.user_profile = get_user_profile(resume_path)
    state.job_profile = get_job_profile(jd_path)

def resume_screening(state: State):
    return{'resume_score':get_resume_score(state.user_profile ,state.job_profile['summary'] ,state.user_profile['skills'],state.job_profile['skills'])}

def interview_condition(state: State):
    if state.resume_score > 0.6:
        return True
    else:
        return False

def interview(state:State):
    return {'chats':run_interview(state.user_profile , state.job_profile)}

def resume_enhancements(state: State):
    return {'enhanced_resume_path': get_enhanced_resume(state.user_profile , state.job_profile)}

def evaluator(state: State):
    pass

agent = StateGraph(State)

agent.add_node('inputs',inputs)
agent.add_node('resume_screening',resume_screening)
agent.add_node('interview_condition',interview_condition)
agent.add_node('resume_enhancements',resume_enhancements)
agent.add_node('interview',interview)
agent.add_node('evaluator',evaluator)

agent.add_edge(START , 'inputs')
agent.add_edge('inputs','resume_screening')
agent.add_conditional_edges('resume_screening',interview_condition,{True:'interview',False:'resume_enhancements'})
agent.add_edge('resume_enhancements', END)
agent.add_edge('interview','evaluator')
agent.add_edge('evaluator',END)