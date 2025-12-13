import os
import time
from typing import TypedDict, Annotated, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.messages import trim_messages

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

load_dotenv()

# -------------------------------------------------
# ENV
# -------------------------------------------------
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
MODEL = os.getenv("MODEL", "gpt-5-nano")

RECURSION_LIMIT = 3000
MAX_TOKENS = 60000
TIME_LIMIT = 180  # seconds

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

# -------------------------------------------------
# TOOLS
# -------------------------------------------------
TOOLS = [
    get_rendered_html,
    download_file,
    run_code,
    post_request,
    add_dependencies,          # disabled-safe version
    ocr_image_tool,
    transcribe_audio,
    encode_image_to_base64,
]

# -------------------------------------------------
# LLM
# -------------------------------------------------
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4 / 60,
    check_every_n_seconds=1,
    max_bucket_size=4,
)

llm = init_chat_model(
    model=MODEL,
    rate_limiter=rate_limiter,
).bind_tools(TOOLS)

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------
SYSTEM_PROMPT = f"""
You are an autonomous quiz-solving agent.

Your tasks:
1. Load the quiz page from the given URL.
2. Extract instructions, data links, and submit endpoint.
3. Solve the task accurately.
4. Submit the answer ONLY to the specified endpoint.
5. Follow the next URL if provided.
6. Stop only when no new URL is given (output END).

Rules:
- Never hallucinate URLs or fields.
- Always inspect server responses.
- Use tools for HTML rendering, downloads, OCR, audio, or code execution.
- For base64 images, ONLY use encode_image_to_base64 tool.
- Always include:
    email = {EMAIL}
    secret = {SECRET}
"""

# -------------------------------------------------
# AGENT NODE
# -------------------------------------------------
def agent_node(state: AgentState):
    now = time.time()
    cur_url = os.getenv("url")
    start_time = url_time.get(cur_url)

    # ----- HARD TIME CHECK -----
    if start_time and (now - start_time) >= TIME_LIMIT:
        fail_msg = HumanMessage(
            content=(
                "Time limit exceeded. "
                "Immediately call post_request with an incorrect answer."
            )
        )
        result = llm.invoke(state["messages"] + [fail_msg])
        return {"messages": [result]}

    # ----- CONTEXT TRIMMING -----
    trimmed = trim_messages(
        messages=state["messages"],
        max_tokens=MAX_TOKENS,
        strategy="last",
        include_system=True,
        start_on="human",
        token_counter=llm,
    )

    if not any(m.type == "human" for m in trimmed):
        reminder = HumanMessage(
            content=f"Continue solving quiz at URL: {cur_url}"
        )
        trimmed.append(reminder)

    result = llm.invoke(trimmed)
    return {"messages": [result]}

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
def route(state: AgentState):
    last = state["messages"][-1]

    # Tool call
    if getattr(last, "tool_calls", None):
        return "tools"

    # END condition
    content = getattr(last, "content", None)
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

    print("Quiz processing completed.")
