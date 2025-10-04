import logging
import os, json
from mcp import types
from adapters import FinamAPIClient


def get_client(access_token) -> FinamAPIClient:
    _client = FinamAPIClient(os.getenv("FINAM_ACCESS_TOKEN"))
    return _client


def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="finam_get_quote",
            description="Получение текущей котировки инструмента",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Тикер, например SBER@MISX"}
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="finam_get_orderbook",
            description="Получение стакана по инструменту",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "depth": {"type": "integer", "default": 10},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="finam_get_candles",
            description="Получение исторических свечей",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string", "default": "D"},
                    "start": {"type": "string", "description": "Начало периода ISO8601"},
                    "end": {"type": "string", "description": "Конец периода ISO8601"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="finam_get_account",
            description="Получение информации о счете",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                },
                "required": ["account_id"],
            },
        ),
        types.Tool(
            name="finam_get_orders",
            description="Получение списка ордеров",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                },
                "required": ["account_id"],
            },
        ),
        types.Tool(
            name="finam_get_order",
            description="Получение информации об ордере",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "order_id": {"type": "string"},
                },
                "required": ["account_id", "order_id"],
            },
        ),
        types.Tool(
            name="finam_create_order",
            description="Создание нового ордера",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "order_data": {"type": "object", "description": "JSON-данные ордера"},
                },
                "required": ["account_id", "order_data"],
            },
        ),
        types.Tool(
            name="finam_cancel_order",
            description="Отмена ордера",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "order_id": {"type": "string"},
                },
                "required": ["account_id", "order_id"],
            },
        ),
        types.Tool(
            name="finam_get_trades",
            description="Получение истории сделок",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                    "start": {"type": "string", "description": "Начало периода ISO8601"},
                    "end": {"type": "string", "description": "Конец периода ISO8601"},
                },
                "required": ["account_id"],
            },
        ),
        types.Tool(
            name="finam_get_positions",
            description="Получение открытых позиций",

            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string"},
                },
                "required": ["account_id"],
            },
        ),
        types.Tool(
            name="finam_get_session_details",
            description="Получение деталей текущей сессии",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },

        ),
    ]

def call_tool(name: str, arguments: dict):
    try:
        client = get_client(arguments['FINAM_ACCESS_TOKEN'])

        if name == "finam_get_quote":
            data = client.get_quote(arguments["symbol"])

        elif name == "finam_get_orderbook":
            data = client.get_orderbook(arguments["symbol"], arguments.get("depth", 10))

        elif name == "finam_get_candles":
            data = client.get_candles(
                arguments["symbol"],
                arguments.get("timeframe", "D"),
                arguments.get("start"),
                arguments.get("end"),
            )

        elif name == "finam_get_account":
            data = client.get_account(arguments["account_id"])

        elif name == "finam_get_orders":
            data = client.get_orders(arguments["account_id"])

        elif name == "finam_get_order":
            data = client.get_order(arguments["account_id"], arguments["order_id"])

        elif name == "finam_create_order":
            data = client.create_order(arguments["account_id"], arguments["order_data"])

        elif name == "finam_cancel_order":
            data = client.cancel_order(arguments["account_id"], arguments["order_id"])

        elif name == "finam_get_trades":
            data = client.get_trades(
                arguments["account_id"],
                arguments.get("start"),
                arguments.get("end"),
            )

        elif name == "finam_get_positions":
            data = client.get_positions(arguments["account_id"])

        elif name == "finam_get_session_details":
            data = client.get_session_details()

        else:
            raise ValueError(f"Unknown tool: {name}")
        logging.info(24242)
        return [types.TextContent(type="text", text=json.dumps(data, indent=2))]
    except Exception as e:
        print(e.args, e)
