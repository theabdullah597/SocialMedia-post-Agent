from typing import TypedDict

class AgentState(TypedDict, total=False):
    # User Request
    topic: str
    audience: str
    platform: str
    tone: str
    length: str
    content_type: str

    # Research
    knowledge: str
    web_information: str
    research_iterations: int
    research_gaps: str
    sources: list

    # Agent Output
    plan: str
    draft: str
    critique: str

    # Control
    revision_needed: bool
    revision_count: int
    unsupported_claims: list
    human_feedback: str

    # Final Result
    final_content: str
