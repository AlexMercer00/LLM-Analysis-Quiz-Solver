from langgraph.graph import StateGraph, END, START
from shared_store import url_time
import time
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.prebuilt import ToolNode
from tools import (
    get_rendered_html,
    download_file,
    post_request,
    run_code,
    add_dependencies,
    ocr_image_tool,
    transcribe_audio,
    encode_image_to_base64,
)
from typing import TypedDict, Annotated, List
from langchain_core.messages import trim_messages, HumanMessage
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
MODEL = os.getenv("MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing")

RECURSION_LIMIT = 2000
MAX_TOKENS = 60000

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

TOOLS = [
    run_code,
    get_rendered_html,
    download_file,
    post_request,
    add_dependencies,
    ocr_image_tool,
    transcribe_audio,
    encode_image_to_base64,
]

# -------------------------------------------------
# LLM INIT (GEMINI ONLY)
# -------------------------------------------------
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4 / 60,
    check_every_n_seconds=1,
    max_bucket_size=4,
)

llm = init_chat_model(
    model=MODEL,
    model_provider="google_genai",
    rate_limiter=rate_limiter,
).bind_tools(TOOLS)

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent.

Rules:
- Always read instructions from the page carefully.
- Use tools for JavaScript rendering, downloads, OCR, audio, and analysis.
- Submit answers ONLY to the submit endpoint specified on the page.
- Never hallucinate URLs or fields.
- Follow any new URLs until none remain.
- Always include:
  email = {EMAIL}
  secret = {SECRET}
"""

# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    cur_time = time.time()
    cur_url = os.getenv("url")
    prev_time = url_time.get(cur_url)

    # Hard 3-minute limit
    if prev_time and (cur_time - prev_time) >= 180:
        fail_msg = HumanMessage(
            content="Time limit exceeded. Immediately submit an incorrect answer."
        )
        result = llm.invoke(state["messages"] + [fail_msg])
        return {"messages": [result]}

    trimmed = trim_messages(
        messages=state["messages"],
        max_tokens=MAX_TOKENS,
        strategy="last",
        include_system=True,
        start_on="human",
        token_counter=llm,
    )

    result = llm.invoke(trimmed)
    return {"messages": [result]}

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
def route(state):
    last = state["messages"][-1]

    if getattr(last, "tool_calls", None):
        return "tools"

    content = getattr(last, "content", "")
    if isinstance(content, str) and content.strip() == "END":
        return END

    return "agent"

# -------------------------------------------------
# GRAPH
# -------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(TOOLS))

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")

graph.add_conditional_edges(
    "agent",
    route,
    {
        "tools": "tools",
        "agent": "agent",
        END: END,
    },
)

app = graph.compile()

# -------------------------------------------------
# RUNNER
# -------------------------------------------------
def run_agent(url: str):
    initial_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": url},
    ]

    app.invoke(
        {"messages": initial_messages},
        config={"recursion_limit": RECURSION_LIMIT},
    )
