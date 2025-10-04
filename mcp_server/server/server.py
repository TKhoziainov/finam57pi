import json, logging, time
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from tools import call_tool, list_tools
from adapters import FinamAPIClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
tool_logger = logging.getLogger("mcp.tools")
uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_access = logging.getLogger("uvicorn.access")
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("mcp.server.lowlevel").setLevel(logging.DEBUG)
uvicorn_error.setLevel(logging.INFO)
uvicorn_access.setLevel(logging.INFO)

server = FastMCP(
    name="finam_mcp",
    host="0.0.0.0",
    port=8010
)

api = FinamAPIClient()
api.register_tools(server)

if __name__ == "__main__":
    server.run(transport="sse", mount_path="/")
