from testing import agent

from fastapi import FastAPI
app = FastAPI()


@app.post("/start")
def start_process(thread_id: str):
    """Triggers the graph. It will run 'generator' and stop at 'updator'."""
    config = {"configurable": {"thread_id": thread_id}}
    agent.invoke({"msg": "initial"}, config)
    return {"status": "Paused at 'updator'. Please call /submit-answer"}


@app.post("/submit-answer")
def submit_answer(thread_id: str, answer: str):
    config = {"configurable": {"thread_id": thread_id}}

    # 1. Check if the thread is already finished before doing anything
    pre_snapshot = agent.get_state(config)
    if not pre_snapshot.next:
        return {"status": "Error", "message": "Thread already finished. Start a new one."}

    # 2. Update the state with the user's answer
    # This acts as the "input" for the updator node
    agent.update_state(config, {"msg": answer})

    # 3. Resume the graph and capture the outputs
    latest_output = {}
    # We stream so we can see the path the graph takes
    for output in agent.stream(None, config, stream_mode="updates"):
        latest_output = output
        # Print to console for server-side debugging
        print(f"Step output: {output}")

    # 4. Check the state after the stream finishes
    post_snapshot = agent.get_state(config)

    # 5. Determine if we are at END or paused again
    if not post_snapshot.next:
        return {
            "status": "Flow Finished",
            "final_state": post_snapshot.values
        }
    else:
        return {
            "status": "Paused",
            "current_data": post_snapshot.values,
            "next_node": post_snapshot.next
        }