import sys
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the parent directory to the path so we can import graph.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph import build_graph

app = FastAPI(title="AI Content Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the global agent
agent = build_graph()

class GenerateRequest(BaseModel):
    topic: str
    audience: str
    platform: str
    tone: str
    length: str
    content_type: str

class ReviseRequest(BaseModel):
    thread_id: str
    feedback: str

class ApproveRequest(BaseModel):
    thread_id: str

@app.post("/generate")
def generate_content(req: GenerateRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "topic": req.topic,
        "audience": req.audience,
        "platform": req.platform,
        "tone": req.tone,
        "length": req.length,
        "content_type": req.content_type,
        "revision_count": 0,
        "research_iterations": 0
    }
    
    # Run the graph until it interrupts at human_review
    for event in agent.stream(initial_state, config=config):
        pass
        
    state = agent.get_state(config).values
    
    return {
        "thread_id": thread_id,
        "draft": state.get("draft", ""),
        "plan": state.get("plan", ""),
        "critique": state.get("critique", ""),
        "sources": state.get("sources", []),
        "revision_count": state.get("revision_count", 0),
        "platform": state.get("platform", ""),
        "status": "waiting_for_review"
    }

@app.post("/revise")
def revise_content(req: ReviseRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    
    # Check if thread exists
    state = agent.get_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Update the state with human feedback
    agent.update_state(config, {"human_feedback": req.feedback})
    
    # Resume the graph
    for event in agent.stream(None, config=config):
        pass
        
    updated_state = agent.get_state(config).values
    
    return {
        "thread_id": req.thread_id,
        "draft": updated_state.get("draft", ""),
        "plan": updated_state.get("plan", ""),
        "critique": updated_state.get("critique", ""),
        "sources": updated_state.get("sources", []),
        "revision_count": updated_state.get("revision_count", 0),
        "platform": updated_state.get("platform", ""),
        "status": "waiting_for_review"
    }

@app.post("/approve")
def approve_content(req: ApproveRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    
    state = agent.get_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    agent.update_state(config, {"human_feedback": "approve"})
    
    # Resume the graph, it will route to finalize and END
    for event in agent.stream(None, config=config):
        pass
        
    final_state = agent.get_state(config).values
    
    return {
        "final_content": final_state.get("final_content", ""),
        "status": "completed"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
