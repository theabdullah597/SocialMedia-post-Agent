import json
from state import AgentState
from research import research
from tools import research_topic
from llm import generate_text
from logger import log_event

PLATFORM_RULES = {
    "LinkedIn": [
        "professional tone",
        "educational focus",
        "structured with clear spacing",
        "strong opening hook",
        "useful insights",
        "moderate use of hashtags"
    ],
    "Instagram": [
        "highly engaging",
        "concise and caption-friendly",
        "easy to scan visually",
        "very strong visual hook",
        "suitable and relevant hashtags"
    ],
    "X/Twitter": [
        "extremely concise",
        "strong opening sentence",
        "short paragraphs",
        "format as a thread if the topic requires length"
    ],
    "Facebook": [
        "conversational tone",
        "educational yet accessible",
        "highly readable",
        "community-oriented and encouraging comments"
    ]
}

def research_node(state: AgentState):
    log_event("RESEARCH", "START", "Starting...")
    topic = state["topic"]
    
    result = research(topic)
    
    log_event("RESEARCH", "QDRANT", "Knowledge retrieved.")
    log_event("RESEARCH", "TAVILY", "Web information retrieved.")
    
    return {
        "knowledge": result["knowledge"],
        "web_information": result["web_information"],
        "sources": result.get("sources", [])
    }

def evaluate_research_node(state: AgentState):
    log_event("EVALUATE RESEARCH", "CHECK", "Checking if information is sufficient...")
    topic = state.get("topic", "")
    audience = state.get("audience", "")
    knowledge = state.get("knowledge", "")
    web_info = state.get("web_information", "")
    
    prompt = f"""
    You are a research evaluator for an AI content agent.
    Your job is to determine if the retrieved research is sufficient to write a high-quality educational social media post.
    
    TOPIC: {topic}
    TARGET AUDIENCE: {audience}
    
    PRIVATE KNOWLEDGE BASE:
    {knowledge}
    
    WEB RESEARCH:
    {web_info}
    
    Consider:
    1. Is the information sufficient to explain the topic?
    2. Are there conflicting facts that need clarification?
    3. Are important claims unsupported?
    4. Is the available knowledge too weak or generic?
    
    Return a STRICT JSON object with no markdown formatting:
    {{
        "sufficient": <boolean>,
        "gaps": "<string explaining what is missing or needs clarification, empty if sufficient>"
    }}
    """
    
    response = generate_text(prompt)
    
    try:
        clean_json = response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        eval_data = json.loads(clean_json.strip())
        sufficient = eval_data.get("sufficient", True)
        gaps = eval_data.get("gaps", "")
        
        log_event("EVALUATE RESEARCH", "RESULT", f"Sufficient: {sufficient}")
        if not sufficient:
            log_event("EVALUATE RESEARCH", "GAPS", f"Identified gaps: {gaps}")
            
        return {
            "research_gaps": gaps if not sufficient else "",
        }
    except Exception as e:
        log_event("EVALUATE RESEARCH", "ERROR", f"Failed to parse JSON: {e}")
        return {"research_gaps": ""}

def deep_research_node(state: AgentState):
    iterations = state.get("research_iterations", 0)
    log_event("DEEP RESEARCH", "START", f"Iteration {iterations + 1}...")
    
    gaps = state.get("research_gaps", "")
    topic = state.get("topic", "")
    
    query = f"{topic} {gaps}"
    
    web_results = research_topic(query)
    
    new_info = "\\n\\n".join(
        result["content"]
        for result in web_results
    )
    
    new_sources = [
        {
            "title": res.get("title", ""),
            "url": res.get("url", ""),
            "content": res.get("content", "")
        }
        for res in web_results
    ]
    
    current_web_info = state.get("web_information", "")
    updated_web_info = current_web_info + "\\n\\n--- ADDITIONAL RESEARCH ---\\n" + new_info
    
    current_sources = state.get("sources", [])
    current_sources.extend(new_sources)
    
    log_event("DEEP RESEARCH", "TAVILY", "Additional web information retrieved for gaps.")
    
    return {
        "web_information": updated_web_info,
        "research_iterations": iterations + 1,
        "sources": current_sources
    }

def planner_node(state: AgentState):
    log_event("PLANNER", "START", "Strategy generating...")
    topic = state.get("topic", "")
    audience = state.get("audience", "")
    platform = state.get("platform", "")
    tone = state.get("tone", "")
    length = state.get("length", "")
    content_type = state.get("content_type", "educational post")
    knowledge = state.get("knowledge", "")
    web_info = state.get("web_information", "")
    
    # Retrieve platform-specific rules
    platform_rules = PLATFORM_RULES.get(platform, ["Follow general best practices for social media."])
    platform_rules_text = "\\n".join(f"- {rule}" for rule in platform_rules)
    
    prompt = f"""
    You are the strategic planning component of an autonomous educational social-media content agent.
    Your job is NOT to write the final post.
    Your job is to analyze the available research and create a strong content strategy for another AI component that will write the post.

    TOPIC: {topic}
    TARGET AUDIENCE: {audience}
    PLATFORM: {platform}
    TONE: {tone}
    LENGTH: {length}
    CONTENT TYPE: {content_type}

    PLATFORM SPECIFIC STRATEGY RULES:
    {platform_rules_text}

    PRIVATE KNOWLEDGE BASE:
    {knowledge}

    WEB RESEARCH:
    {web_info}

    Create a content plan containing:
    1. Main educational angle
    2. Target audience problem or curiosity
    3. Hook strategy
    4. Key points to explain
    5. Example or analogy to use
    6. Suggested content structure
    7. Important facts that should be preserved
    8. Things the writer should avoid
    9. Suggested call-to-action

    Rules:
    - Base the strategy on the provided research.
    - Do not invent facts.
    - Prioritize educational value.
    - Adapt the strategy strictly to the PLATFORM SPECIFIC STRATEGY RULES above.
    - Structure the plan specifically for a {content_type} format.
    - Keep the plan practical for the writer.
    - Do not write the final social-media post.
    """
    
    plan = generate_text(prompt)
    log_event("PLANNER", "DONE", "Strategy generated.")
    return {"plan": plan}

def writer_node(state: AgentState):
    log_event("WRITER", "START", "Draft generating...")
    topic = state.get("topic", "")
    audience = state.get("audience", "")
    platform = state.get("platform", "")
    tone = state.get("tone", "")
    length = state.get("length", "")
    content_type = state.get("content_type", "educational post")
    knowledge = state.get("knowledge", "")
    web_info = state.get("web_information", "")
    plan = state.get("plan", "")

    # Retrieve platform-specific rules
    platform_rules = PLATFORM_RULES.get(platform, ["Follow general best practices for social media."])
    platform_rules_text = "\\n".join(f"- {rule}" for rule in platform_rules)

    prompt = f"""
    You are an expert educational social media content writer.
    Your task is to write a polished social media post based on the provided strategy and research.

    TOPIC: {topic}
    TARGET AUDIENCE: {audience}
    PLATFORM: {platform}
    TONE: {tone}
    LENGTH: {length}
    CONTENT TYPE: {content_type}
    
    PLATFORM SPECIFIC WRITING RULES:
    {platform_rules_text}

    CONTENT STRATEGY / PLAN:
    {plan}

    AVAILABLE RESEARCH:
    Private Knowledge: {knowledge}
    Web Information: {web_info}

    Rules:
    - Follow the PLATFORM SPECIFIC WRITING RULES closely for {platform}.
    - Format the post strictly as a {content_type}.
    - Follow the requested tone ({tone}) and length ({length}).
    - Do not invent facts or make unsupported claims. Use ONLY the provided research.
    - Provide ONLY the final social media post content. Do not include introductory text like "Here is the post:".
    """
    
    draft = generate_text(prompt)
    log_event("WRITER", "DONE", "Draft generated.")
    return {"draft": draft}

def critic_node(state: AgentState):
    log_event("CRITIC", "START", "Evaluating draft...")
    topic = state.get("topic", "")
    audience = state.get("audience", "")
    platform = state.get("platform", "")
    draft = state.get("draft", "")
    plan = state.get("plan", "")
    knowledge = state.get("knowledge", "")
    web_info = state.get("web_information", "")

    prompt = f"""
    You are an expert content critic for educational social media posts.
    Evaluate the following draft based on the original plan, platform, and audience.
    
    AVAILABLE RESEARCH (Use this to fact-check):
    {knowledge}
    {web_info}

    TOPIC: {topic}
    TARGET AUDIENCE: {audience}
    PLATFORM: {platform}

    CONTENT PLAN:
    {plan}

    DRAFT TO EVALUATE:
    {draft}

    Evaluate the draft on:
    - Factual accuracy explicitly checked against the AVAILABLE RESEARCH.
    - For each important factual claim in the draft, classify it as SUPPORTED, UNSUPPORTED, or UNCERTAIN based ONLY on the provided research.
    - Relevance and educational value
    - Clarity and readability
    - Hook quality and CTA quality
    - Structure and platform suitability

    You MUST return your evaluation STRICTLY as a JSON object with the following schema, and no other text:
    {{
        "score": <integer from 0 to 100>,
        "unsupported_claims": ["list of strings containing any UNSUPPORTED or UNCERTAIN claims, empty if none"],
        "strengths": ["list of strengths"],
        "weaknesses": ["list of weaknesses"],
        "required_improvements": ["list of things to fix"],
        "revision_needed": <boolean, true if score < 85 or there are unsupported claims, false otherwise>
    }}
    """
    
    response = generate_text(prompt)
    
    try:
        # Clean up the response in case the LLM wraps it in markdown code blocks
        clean_json = response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        clean_json = clean_json.strip()
        critique_data = json.loads(clean_json)
        
        score = critique_data.get("score", 0)
        revision_needed = critique_data.get("revision_needed", True)
        unsupported_claims = critique_data.get("unsupported_claims", [])
        
        log_event("CRITIC", "RESULT", f"Score: {score}")
        if unsupported_claims:
            log_event("CRITIC", "WARN", f"Found {len(unsupported_claims)} unsupported claims!")
        
        return {
            "critique": json.dumps(critique_data, indent=2),
            "revision_needed": revision_needed,
            "unsupported_claims": unsupported_claims
        }
        
    except Exception as e:
        log_event("CRITIC", "ERROR", f"Failed to parse JSON: {e}")
        return {
            "critique": response,
            "revision_needed": True,
            "unsupported_claims": []
        }

def fact_check_research_node(state: AgentState):
    unsupported_claims = state.get("unsupported_claims", [])
    if not unsupported_claims:
        return {}
        
    log_event("FACT CHECK", "START", f"Researching {len(unsupported_claims)} unsupported claims...")
    topic = state.get("topic", "")
    new_info_blocks = []
    current_sources = state.get("sources", [])
    
    for claim in unsupported_claims:
        query = f"{topic} {claim} fact check"
        results = research_topic(query)
        new_info = "\\n\\n".join(result["content"] for result in results)
        new_info_blocks.append(f"--- FACT CHECK RESEARCH FOR: {claim} ---\\n{new_info}")
        
        new_sources = [
            {
                "title": res.get("title", ""),
                "url": res.get("url", ""),
                "content": res.get("content", "")
            }
            for res in results
        ]
        current_sources.extend(new_sources)
        
    current_web_info = state.get("web_information", "")
    updated_web_info = current_web_info + "\\n\\n" + "\\n\\n".join(new_info_blocks)
    
    log_event("FACT CHECK", "DONE", "Fact check research completed.")
    
    return {
        "web_information": updated_web_info,
        "sources": current_sources
    }

def revision_node(state: AgentState):
    current_revisions = state.get("revision_count", 0)
    log_event("REVISION", "START", f"Revision {current_revisions + 1}...")
    
    topic = state.get("topic", "")
    draft = state.get("draft", "")
    critique = state.get("critique", "")
    plan = state.get("plan", "")
    knowledge = state.get("knowledge", "")
    web_info = state.get("web_information", "")
    
    prompt = f"""
    You are an expert social media content editor.
    Your task is to revise a draft social media post based on the provided critique.

    TOPIC: {topic}
    
    ORIGINAL PLAN:
    {plan}
    
    AVAILABLE RESEARCH:
    Private Knowledge: {knowledge}
    Web Information: {web_info}

    CURRENT DRAFT:
    {draft}

    CRITIQUE & REQUIRED IMPROVEMENTS:
    {critique}

    Rules:
    - Address all weaknesses and required improvements from the critique.
    - Fix any factual issues.
    - Preserve the correct information and strengths of the original draft.
    - Provide ONLY the revised final social media post content. Do not include introductory text.
    """
    
    revised_draft = generate_text(prompt)
    
    return {
        "draft": revised_draft,
        "revision_count": current_revisions + 1
    }

def human_review_node(state: AgentState):
    log_event("HUMAN REVIEW", "PAUSED", "Waiting for human approval or feedback...")
    return {}

def human_revision_node(state: AgentState):
    log_event("HUMAN REVISION", "START", "Applying human feedback...")
    draft = state.get("draft", "")
    feedback = state.get("human_feedback", "")
    plan = state.get("plan", "")
    
    prompt = f"""
    You are an expert social media content editor.
    The user has reviewed the draft and requested the following changes:
    
    USER FEEDBACK:
    {feedback}
    
    CURRENT DRAFT:
    {draft}
    
    ORIGINAL PLAN:
    {plan}
    
    Rules:
    - Apply the user's feedback precisely.
    - Preserve the strengths of the original draft unless they conflict with the feedback.
    - Provide ONLY the revised social media post content.
    """
    
    revised_draft = generate_text(prompt)
    
    return {
        "draft": revised_draft,
        "human_feedback": "", # Clear it so we don't loop infinitely
        "revision_count": state.get("revision_count", 0) + 1
    }

def finalize_node(state: AgentState):
    log_event("FINALIZE", "DONE", "Content finalized.")
    return {
        "final_content": state.get("draft", "")
    }

if __name__ == "__main__":
    # Test script to run the nodes sequentially without LangGraph yet
    test_state = {
        "topic": "Retrieval Augmented Generation",
        "audience": "Beginner AI engineers",
        "platform": "LinkedIn",
        "tone": "Educational",
        "length": "Medium",
        "content_type": "myth vs fact",
        "revision_count": 0
    }

    print("--- TESTING NODES ---")
    
    # 1. Research
    research_result = research_node(test_state)
    test_state.update(research_result)
    
    # 2. Planner
    plan_result = planner_node(test_state)
    test_state.update(plan_result)
    
    # 3. Writer
    writer_result = writer_node(test_state)
    test_state.update(writer_result)
    
    # 4. Critic
    critic_result = critic_node(test_state)
    test_state.update(critic_result)
    
    print("\n===== FINAL DRAFT DUMP =====")
    print(test_state["draft"])
    print("\n===== CRITIQUE DUMP =====")
    print(test_state["critique"])
    print(f"\nRevision Needed: {test_state['revision_needed']}")