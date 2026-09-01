from retrieve import search_knowledge
from llm import generate_text

def answer_from_knowledge(query):
    result=search_knowledge(query,k=3)
    context="\n\n".join(
        document.page_content
        for document in result
    )

    prompt=f"""
    You are an educational AI assistant.

   Answer the user's question using the provided context.

    CONTEXT:
    {context}
    
    USER QUESTION:
    {query}
    
    Instructions:
    - Use the context as your main source of information.
    - Do not invent information that is not supported by the context.
    - If the context does not contain enough information, say so.
    - Explain the answer clearly and simply.
        """
    return generate_text(prompt)

if __name__=="__main__":
    query=input("Enter a question:")
    answer=answer_from_knowledge(query)
    print("\n=====Answer=====\n")
    print(answer)