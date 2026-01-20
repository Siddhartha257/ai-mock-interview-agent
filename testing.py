#%%
from pydantic import BaseModel
from langgraph.graph import START , StateGraph , END
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
class State(BaseModel):
    msg : str
def generator(state : State):
    return {'msg':"this is initial message"}

def updator(state : State):
    return {'msg':state.msg}

def final(state : State):
    return {'msg':state.msg}

def condition(state : State):
    if state.msg =="end":
        return True
    else:
        return False

workflow = StateGraph(State)
workflow.add_node("generator", generator)
workflow.add_node("updator", updator)
workflow.add_node("final", final)


workflow.add_edge(START, "generator")
workflow.add_edge("generator","updator")
workflow.add_conditional_edges("updator",condition , {True : END , False : "final"})
workflow.add_edge("final","updator")

agent = workflow.compile(checkpointer=checkpointer, interrupt_before=["updator" , "final"])

# initial_input = {"msg": "Starting process..."}
# for output in agent.stream(initial_input):
#     print(output)