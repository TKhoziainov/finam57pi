# analysts/graph.py
import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from .state import State, UserCommand, Code

api_key = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    model="gpt-4o-mini",
)

mcp_client = MultiServerMCPClient(
    connections={"finam_mcp": {"url": "http://finam-mcp-server:8010/sse", "transport": "sse"}}
)

_docs = ""
_tools = None
_graph = None
_lock = asyncio.Lock()

def create_chatbot(system_prompt: str, llm_obj: ChatOpenAI, tools=None):
    tooled = llm_obj.bind_tools(tools) if tools else llm_obj
    async def chatbot(state: State):
        msgs = [{"role": "system", "content": system_prompt}] + state["messages"]
        return {"messages": [await tooled.ainvoke(msgs)]}
    return chatbot

router_llm = llm.with_structured_output(UserCommand)

async def router(state: State):
    return {"user_command": await router_llm.ainvoke(state["messages"]), "messages": state["messages"]}

def react_to_command(state: State):
    return "chatbot" if state["user_command"]["command"] == "chat" else "planner"

def route_tools(state: State):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError("no messages")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

strategy_metrics = """
Strategy metrics:
Annualized Return (CAGR)
Volatility
Value at Risk
Sharpe Ratio
Equity Curve Smoothness
"""

async def code(state: State):
    sp = "You are a python developer. You are given a discription of a pyton script that generates metrics based on a trading strategy. You need to write a python script that implements this strategy. You can only use finam api to get data. You cant talk"
    msgs = [{"role": "system", "content": sp}] + state["messages"] + [{"role": "user", "content": f"docs: {_docs}"}]
    return {"code": await llm.with_structured_output(Code).ainvoke(msgs)}

def build_graph(tools):
    gb = StateGraph(State)
    chatbot = create_chatbot(
        "You are an assistant that helps with trading. You can use the following tools to help the user and trade for him.",
        llm,
        tools,
    )
    planner = create_chatbot(
        "You are a manager. Your task is to create a discription of a pyton script that generates this metrics based on a trading strategy."
        + strategy_metrics,
        llm,
        None,
    )
    gb.add_node("chatbot", chatbot)
    gb.add_node("planner", planner)
    gb.add_node("code", code)
    gb.add_node("router", router)
    gb.add_node("tools", ToolNode(tools))
    gb.add_edge(START, "router")
    gb.add_conditional_edges("router", react_to_command)
    gb.add_conditional_edges("chatbot", route_tools)
    gb.add_edge("tools", "chatbot")
    gb.add_edge("planner", "code")
    gb.add_edge("code", END)
    gb.add_edge("planner", END)
    return gb.compile()

async def init_tools():
    return await mcp_client.get_tools()

async def get_graph():
    global _graph, _tools
    if _graph is None:
        async with _lock:
            if _graph is None:
                _tools = await init_tools()
                _graph = build_graph(_tools)
    return _graph

def set_docs(text: str):
    global _docs
    _docs = text
