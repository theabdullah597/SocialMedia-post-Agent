from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from logger import log_event
from nodes import (
    research_node,
    evaluate_research_node,
    deep_research_node,
    planner_node,
    writer_node,
    critic_node,
    fact_check_research_node,
    revision_node,
    human_review_node,
    human_revision_node,
    finalize_node
)

MAX_REVISIONS = 3
MAX_RESEARCH_ITERATIONS = 2

def should_revise(state: AgentState):
    """
    Conditional routing function to determine the next step after the critic node.
    """
    revision_needed = state.get("revision_needed", False)
    revision_count = state.get("revision_count", 0)
    unsupported_claims = state.get("unsupported_claims", [])
    
    log_event("GRAPH", "ROUTE", f"Revision needed: {revision_needed}, Current count: {revision_count}")
    
    if revision_needed and revision_count < MAX_REVISIONS:
        if unsupported_claims:
            log_event("GRAPH", "ROUTE", f"Found {len(unsupported_claims)} unsupported claims. Routing to fact check.")
            return "fact_check"
        return "revise"
    else:
        if revision_count >= MAX_REVISIONS:
            log_event("GRAPH", "ROUTE", "Maximum revisions reached. Routing to human review.")
        return "human_review"

def should_deep_research(state: AgentState):
    """
    Conditional routing function to determine if more research is needed.
    """
    gaps = state.get("research_gaps", "")
    iterations = state.get("research_iterations", 0)
    
    if gaps and iterations < MAX_RESEARCH_ITERATIONS:
        log_event("GRAPH", "ROUTE", "Research insufficient. Routing to deep research.")
        return "research_again"
    else:
        if iterations >= MAX_RESEARCH_ITERATIONS:
            log_event("GRAPH", "ROUTE", "Maximum research iterations reached.")
        else:
            log_event("GRAPH", "ROUTE", "Research sufficient. Continuing to planning.")
        return "continue_to_planning"

def should_human_revise(state: AgentState):
    """
    Conditional routing function after human review.
    """
    feedback = state.get("human_feedback", "")
    if feedback and feedback.strip().lower() != "approve":
        log_event("GRAPH", "ROUTE", f"Human feedback received: {feedback}. Routing to human revision.")
        return "human_revise"
    log_event("GRAPH", "ROUTE", "Content approved by human. Routing to finalize.")
    return "finalize"

def build_graph():
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("evaluate_research", evaluate_research_node)
    workflow.add_node("deep_research", deep_research_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("fact_check_research", fact_check_research_node)
    workflow.add_node("revision", revision_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("human_revision", human_revision_node)
    workflow.add_node("finalize", finalize_node)
    
    # Define edges
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "evaluate_research")
    
    # Add conditional edge for research evaluation
    workflow.add_conditional_edges(
        "evaluate_research",
        should_deep_research,
        {
            "research_again": "deep_research",
            "continue_to_planning": "planner"
        }
    )
    
    # Link deep research back to evaluate research to create a feedback loop
    workflow.add_edge("deep_research", "evaluate_research")
    
    # Continue the pipeline
    workflow.add_edge("planner", "writer")
    workflow.add_edge("writer", "critic")
    
    # Add conditional edge for the critic node
    workflow.add_conditional_edges(
        "critic",
        should_revise,
        {
            "fact_check": "fact_check_research",
            "revise": "revision",
            "human_review": "human_review"
        }
    )
    
    # Link fact check to revision
    workflow.add_edge("fact_check_research", "revision")
    
    # Link revision back to critic
    workflow.add_edge("revision", "critic")
    
    # Human Review Routing
    workflow.add_conditional_edges(
        "human_review",
        should_human_revise,
        {
            "human_revise": "human_revision",
            "finalize": "finalize"
        }
    )
    
    # Link human revision back to critic for evaluation
    workflow.add_edge("human_revision", "critic")
    
    # Finalize node ends the workflow
    workflow.add_edge("finalize", END)
    
    # Compile the graph with MemorySaver and interrupt_before human_review
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory, interrupt_before=["human_review"])

if __name__ == "__main__":
    import uuid
    # Test script to run the LangGraph workflow
    agent = build_graph()
    
    initial_state = {
        "topic": "Retrieval Augmented Generation",
        "audience": "Beginner AI engineers",
        "platform": "LinkedIn",
        "tone": "Educational",
        "length": "Medium",
        "content_type": "educational post",
        "revision_count": 0,
        "research_iterations": 0
    }
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("=== Starting LangGraph workflow ===")
    
    # Stream the graph execution
    for event in agent.stream(initial_state, config=config):
        for node, state_update in event.items():
            print(f"\\n--- Finished node: {node.upper()} ---\\n")
            
    print("=== GRAPH PAUSED FOR HUMAN REVIEW ===")
    state = agent.get_state(config).values
    print(f"Current Draft:\\n{state.get('draft', '')}\\n")
    
    # Simulate human feedback
    feedback = input("Enter feedback (or type 'approve'): ")
    
    # Update state and resume
    agent.update_state(config, {"human_feedback": feedback})
    print("=== Resuming LangGraph workflow ===")
    for event in agent.stream(None, config=config):
        for node, state_update in event.items():
            print(f"\\n--- Finished node: {node.upper()} ---\\n")
            
    print("=== WORKFLOW COMPLETE ===")
