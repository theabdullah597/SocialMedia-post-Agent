
from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily_client=TavilyClient(api_key=TAVILY_API_KEY)
def research_topic(topic):
    response=tavily_client.search(
        query=topic,
        search_depth="advanced",
        max_results=5
    )
    return response["results"]

if __name__=="__main__":
    topic=input("Enter the topic you would like to search: ")
    results=research_topic(topic)
    for i,result in enumerate(results):
        print(f"Result:{i+1}")
        print(f"Title:{result['title']}")
        print(f"url:{result['url']}")
        print(f"Content:{result['content']}")
