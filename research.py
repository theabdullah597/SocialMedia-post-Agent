from tools import research_topic
from retrieve import search_knowledge

def search_topic(topic):
    rag_result=search_knowledge(topic,k=3)
    knowledge="\n\n".join(
        document.page_content
        for document in rag_result
    )

    web_result=research_topic(topic)
    web_info="\n\n".join(
        result['content']
        for result in web_result
    )
    return {
        "Knowledge":knowledge,
        "Web":web_info
    }

if __name__=="__main__":
    topic=input("Enter topic:")
    results=search_topic(topic)
    print("====Knowledge Base====\n")
    print(results["Knowledge"])
    print("====Web Base====\n")
    print(results["Web"])