import os
import time
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_core.messages import HumanMessage, trim_messages
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

from shared_store import url_time
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

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing")

MODEL = "gemini-2.5-flash"
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
# LLM (DIRECT GEMINI — NO init_chat_model)
# -------------------------------------------------
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4 / 60,
    check_every_n_seconds=1,
    max_bucket_size=4,
)

llm = (
    ChatGoogleGenerativeAI(
        model=MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        max_output_tokens=8192,
        rate_limiter=rate_limiter,
    )
    .bind_tools(TOOLS)
)

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent.

Rules:
- Load and read the quiz page carefully.
- Follow instructions EXACTLY.
- Use tools for JS rendering, downloads, OCR, audio, and computation.
- Submit answers ONLY to the provided submit endpoint.
- Never hallucinate URLs or fields.
- Continue until no new URL is returned.
- Always include:
  email = {EMAIL}
  secret = {SECRET}
"""

# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    cur_url = os.getenv("url")
    now = time.time()

    if cur_url in url_time and now - url_time[cur_url] > 180:
        msg = HumanMessage(
            content="Time limit exceeded. Immediately submit an incorrect answer."
        )
        result = llm.invoke(state["messages"] + [msg])
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
    url_time.clear()
    url_time[url] = time.time()
    os.environ["url"] = url

    app.invoke(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": url},
            ]
        },
        config={"recursion_limit": RECURSION_LIMIT},
    )
