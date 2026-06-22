import os
from dotenv import load_dotenv

load_dotenv()


def search_web(query):
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"results": [], "message": "TAVILY_API_KEY is not configured."}

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)
        max_results = int(os.getenv("TAVILY_MAX_RESULTS", "3"))
        response = client.search(query=query, max_results=max_results)
        return response
    except Exception as exc:
        return {"results": [], "error": str(exc)}
