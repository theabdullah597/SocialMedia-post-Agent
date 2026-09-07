from state import AgentState
from research import research
from llm import generate_text

def research_node(state: AgentState):

    print("Agent is researching............")

    topic = state["topic"]

    result = research(topic)

    return {
        "knowledge": result["knowledge"],
        "web_information": result["web_information"],
    }
def planner_node(state:AgentState):
    print("Agent is planning............")
    topic=state["topic"]
    audience=state["audience"]
    platform=state["platform"]
    tone=state["tone"]
    length=state["length"]
    knowledge=state.get("knowledge")
    web_info=state.get("web_info")
    prompt = f"""
    You are the strategic planning component of an autonomous
    educational social-media content agent.

    Your job is NOT to write the final post.

    Your job is to analyze the available research and create a
    strong content strategy for another AI component that will
    write the post.

    TOPIC:
    {topic}

    TARGET AUDIENCE:
    {audience}

    PLATFORM:
    {platform}

    TONE:
    {tone}

    LENGTH:
    {length}

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
    - Adapt the strategy to the specified platform.
    - Keep the plan practical for the writer.
    - Do not write the final social-media post.
    """
    plan=generate_text(prompt)
    return{
        "plan":plan
    }

if __name__ == "__main__":

    test_state = {
        "topic": "Retrieval Augmented Generation",
        "audience": "Beginner AI engineers",
        "platform": "LinkedIn",
        "tone": "Educational",
        "length": "Medium"
    }

    result = research_node(test_state)
    test_state.update(result)

    #plan result
    plan_result=planner_node(test_state)


    # print("\n--- RESEARCH COMPLETED ---")

    # print("\nKnowledge Base:")
    # print(result["knowledge"])
    #
    # print("\nWeb Information:")
    # print(result["web_information"])
    print("=====Content Plan=======")
    print("="*20)
    print(plan_result)