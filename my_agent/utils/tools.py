import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import tool

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def search_api(query: str) -> list[dict]:
    """
    Use this tool to search the web for URLs and brief summaries (snippets).
    Returns a list of dictionaries containing 'title', 'url', and 'content'.
    Analyze the results and choose the most promising URLs to extract the full text.
    """
    response = tavily_client.search(query=query, search_depth="basic", max_results=5)
    return response.get("results", [])

@tool
def extract_api(url: str) -> str:
    """
    Use this tool to extract the full, deep content of a specific URL.
    Pass the exact URL you obtained from the search_api.
    """
    response = tavily_client.extract(urls=[url])
    results = response.get("results", [])
    if results:
        return results[0].get("raw_content", "Content unavailable.")
    return "Failed to extract text from this URL."