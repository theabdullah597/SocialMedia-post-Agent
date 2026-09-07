from typing import TypedDict

class AgentState(TypedDict,total=False):
    # user request
    topic:str
    audience:str
    platform:str
    tone:str
    length:str

    # Research
    knowledge:str
    web_knowledge:str

    #Agent Output
    plan:str
    draft:str
    critique:str

    #control
    revision_needed:bool

    #Final Result
    final_content:str

    
