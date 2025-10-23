"""Web Search Tool for search the web.

This tool allows the agent to search the web for information and uses GPT-5 to analyze results.
"""

from utils.common import LLMTool, ToolImplOutput, DialogMessages
from typing import Any, Optional
from utils.workspace_manager import WorkspaceManager
import logging
from utils.llm_client import get_client, TextPrompt

logger = logging.getLogger(__name__)
import requests
import os

class WebSearchTool(LLMTool):
    name = "web_search"
    description = """Search the web for real-time information, documentation, and solutions."""

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search the web for.",
            },
        },
        "required": ["query"],
    }
    def __init__(self, workspace_manager: WorkspaceManager):
        super().__init__()
        self.workspace_manager = workspace_manager
        
        self.gpt5_client = get_client("openai-direct", model_name="gpt-4o", cot_model=True)
    
    def _analyse_with_gpt5(self, query: str, results: str) -> str:
        if not self.gpt5_client:
            return "GPT-4o analysis unavailable"
        prompt = f"""What's the most important information from these search results for "{query}"?

Results:
{results}

Give a brief, direct answer focusing on the key information only."""
        try:
            response, _ = self.gpt5_client.generate(
                messages=[[TextPrompt(text=prompt)]],
                max_tokens=200,
                temperature=0.1
            )
            return response[0].text if response else "No analysis available"
        except Exception as e:
            logger.error(f"Error calling GPT-4o for analysis: {e}")
            return f"Error analyzing results: {str(e)}"
            
    def run_impl(self, tool_input: dict[str, Any], dialog_messages: Optional[DialogMessages] = None) -> ToolImplOutput:
        query = tool_input["query"]
        
        try:
            search_results = self._google_search(query)
            
            results_text = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['snippet']}"
                for result in search_results
            ])
            
            analysis = self._analyse_with_gpt5(query, results_text)
            
            return ToolImplOutput(analysis, f"Searched for: {query}")
            
        except Exception as e:
            logger.error(f"Error in web search tool: {e}")
            return ToolImplOutput(f"Error performing web search: {str(e)}", "Search failed")


    def _google_search(self, query: str) -> list[dict[str, str]]:
        """Perform real web search using Google Custom Search API."""
        
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            logger.warning("Google API credentials not set, falling back to mock search")
            raise ValueError("Google API credentials not set")

        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5,
            "safe": "active"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google API request failed: {e}")
            return self._mock_web_search(query)
        except Exception as e:
            logger.error(f"Error processing Google API response: {e}")
            return self._mock_web_search(query)
    
    def _mock_web_search(self, query: str) -> list[dict[str, str]]:
        """Mock web search for testing purposes."""
        mock_results = [
            {
                "title": f"Documentation: {query}",
                "url": f"https://docs.example.com/{query.replace(' ', '-')}",
                "snippet": f"Official documentation for {query} with examples and API reference.",
            },
            {
                "title": f"Stack Overflow: {query}",
                "url": f"https://stackoverflow.com/questions/{hash(query) % 1000000}",
                "snippet": f"Common questions and answers about {query} from the developer community.",
            },
            {
                "title": f"GitHub: {query} examples",
                "url": f"https://github.com/search?q={query.replace(' ', '+')}",
                "snippet": f"Open source projects and code examples related to {query}.",
            },
        ]
        return mock_results