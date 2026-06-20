from tools.tavily_tool import search_web
from dotenv import load_dotenv
from analytics.latency_monitor import start_timer, stop_timer
from analytics.tool_calls import register_tool
from config.llm import invoke_llm

load_dotenv()


def researcher(question):

    start_timer("research_agent")

    register_tool("tavily")

    web_data = search_web(question)

    prompt = f"""
Question:

{question}

Web Search Results:

{web_data}

Provide researched information.
"""

    response = invoke_llm(prompt, task="research")

    stop_timer("research_agent")

    return response
