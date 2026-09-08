from retrieve import search_knowledge
from tools import research_topic


def research(topic):

    # Search our private knowledge base
    rag_results = search_knowledge(topic, k=3)

    knowledge = "\n\n".join(
        document.page_content
        for document in rag_results
    )

    # Search the web
    web_results = research_topic(topic)

    web_information = "\n\n".join(
        result["content"]
        for result in web_results
    )

    sources = [
        {
            "title": res.get("title", ""),
            "url": res.get("url", ""),
            "content": res.get("content", "")
        }
        for res in web_results
    ]

    return {
        "knowledge": knowledge,
        "web_information": web_information,
        "sources": sources
    }