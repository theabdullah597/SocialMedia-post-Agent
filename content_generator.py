from retrieve import search_knowledge
from llm import generate_text

def content_generate(topic,audience,platform,tone,length):
    result=search_knowledge(topic,k=5)
    context="\n\n".join(
        document.page_content
        for document in result
    )
    prompt=f"""You are an expert educational social media content writer.
    Create a {length} {platform} post about:
    TOPIC:s{topic}
    
    TARGET AUDIENCE:
    {audience}
    
    TONE:
    {tone}
    
    Use the following retrieved knowledge as your main source:
    
    CONTEXT:
    {context}
    
    Requirements:
    - Make the content educational and useful.
    - Explain concepts clearly for the target audience.
    - Start with an engaging hook.
    - Use examples where appropriate.
    - Do not invent facts that are not supported by the context.
    - Avoid unnecessary filler.
    - End with a useful takeaway or call to action.
    
    Return only the final social media post."""
    return generate_text(prompt)

if __name__=="__main__":
    topic=input("Enter topic: ")
    audience=input("Enter audience: ")
    platform=input("Enter platform: ")
    tone=input("Enter tone: ")
    length=input("Enter length: ")
    post=content_generate(topic,audience,platform,tone,length)
    print("\n=========Post Generated=======\n")
    print(post)