from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode

from dataclasses import dataclass
from typing import Literal


@dataclass
class UserCommand:
    command: Literal["chat", "analyze_straregy"]


@dataclass
class Code:
    description: str
    imports: str
    code: str

@dataclass
class CodePlan:
    needed_data_from_finam: str
    code_description: str

@dataclass
class CodeAction:
    action: Literal["write_code", "get_finam_data", "end"]

@dataclass
class GraphData:
    x_data: list[float]
    y_data: list[float]
    x_label: str
    y_label: str
    title: str

