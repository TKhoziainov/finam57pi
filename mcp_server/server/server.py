# import asyncio
# from typing import Any
#
# import mcp
# from mcp import types
# from mcp.server.fastmcp import FastMCP
# from tools import call_tool, list_tools
#
# # Создаём сервер MCP
# server = FastMCP(
#     name="finam_mcp",
#     tools=list_tools(),
#     host="0.0.0.0",
#     port=8010
# )
#
# @server.tool()
# def handle_call_tool(name: str, arguments: dict[str, Any]):
#     # return call_tool(name, arguments)
#     try:
#         return call_tool(name, arguments)
#     except Exception as e:
#         return {"error": f"{type(e).__name__}: {e}"}
#
# if __name__ == "__main__":
#     server.run(transport="sse", mount_path="/")
import json, logging, time
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools import call_tool, list_tools
from adapters import FinamAPIClient

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s %(levelname)s %(name)s %(message)s",
#     handlers=[logging.StreamHandler(sys.stdout)],
# )
tool_logger = logging.getLogger("mcp.tools")
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_access = logging.getLogger("uvicorn.access")
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("mcp.server.lowlevel").setLevel(logging.DEBUG)
uvicorn_error.setLevel(logging.INFO)
uvicorn_access.setLevel(logging.INFO)

# def _mask(d: dict[str, Any]) -> dict[str, Any]:
#     keys = {"token","access_token","api_key","password","secret"}
#     return {k: ("***" if k.lower() in keys else v) for k,v in d.items()}

server = FastMCP(
    name="finam_mcp",
    host="0.0.0.0",
    port=8010
)

api = FinamAPIClient()
api.register_tools(server)

if __name__ == "__main__":
    server.run(transport="sse", mount_path="/")
