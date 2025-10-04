import inspect
import logging
import os
import asyncio
import traceback
from pathlib import Path

from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession, types
import json
import streamlit as st
from mcp.client.websocket import websocket_client

from core import call_llm, get_settings


def create_system_prompt() -> str:
    return """Ты - AI ассистент трейдера, работающий с Finam TradeAPI.

Когда пользователь задает вопрос о рынке, портфеле или хочет совершить действие:
1. Определи нужный API endpoint
2. Укажи запрос в формате: API_REQUEST: METHOD /path
3. После получения данных - проанализируй их и дай понятный ответ

Доступные endpoints:
- GET /v1/instruments/{symbol}/quotes/latest - котировка
- GET /v1/instruments/{symbol}/orderbook - стакан
- GET /v1/instruments/{symbol}/bars - свечи
- GET /v1/accounts/{account_id} - счет и позиции
- GET /v1/accounts/{account_id}/orders - ордера
- POST /v1/accounts/{account_id}/orders - создать ордер
- DELETE /v1/accounts/{account_id}/orders/{order_id} - отменить ордер

Отвечай на русском, кратко и по делу."""

def extract_api_request(text: str) -> tuple[str | None, str | None]:
    if "API_REQUEST:" not in text:
        return None, None
    lines = text.split("\n")
    for line in lines:
        if line.strip().startswith("API_REQUEST:"):
            request = line.replace("API_REQUEST:", "").strip()
            parts = request.split(maxsplit=1)
            if len(parts) == 2:
                return parts[0], parts[1]
    return None, None

def _to_schema(s):
    if s is None:
        return {"type": "object", "properties": {}}
    if hasattr(s, "model_dump"):
        return s.model_dump()
    return s

async def run_agent_async(user_query: str):
    url = os.getenv("MCP_SERVER_URL", "http://finam-mcp-server:8010/sse")
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_list = await session.list_tools()
            openai_tools = [{
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": _to_schema(t.inputSchema)
                }
            } for t in tools_list.tools]


            messages = [
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": user_query},
            ]
            while True:
                resp = call_llm(
                    messages=messages,
                    temperature=0.2,
                    tools=openai_tools,
                    tool_choice="auto",
                )
                msg = resp["choices"][0]["message"]

                if not msg.get("tool_calls"):
                    return msg.get("content", "")


                messages.append({"role": "assistant", "tool_calls": msg["tool_calls"]})
                for tc in msg["tool_calls"]:
                    name = tc["function"]["name"]
                    args_json = tc["function"].get("arguments") or "{}"
                    try:
                        args = json.loads(args_json)
                    except Exception:
                        args = {}

                    result = await session.call_tool(name, args)

                    content_parts = getattr(result, "content", []) or []
                    text = "\n".join(
                        p.text for p in content_parts if getattr(p, "type", "") == "text"
                    ) or json.dumps(getattr(result, "result", {}), ensure_ascii=False)

                    # messages.append({
                    #     "role": "tool",
                    #     "tool_call_id": tc["id"],
                    #     "content": text,
                    # })

# async def run_agent_async(user_query: str):
#     url = os.getenv("MCP_SERVER_URL", "http://finam-mcp-server:8010/sse")
#     from mcp.client.sse import sse_client
#
#     async with sse_client(url) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             tools = await session.list_tools()
#             response = call_llm(user_query, temperature=0.3, tools=tools, tool_choice=None)
#             return response["choices"][0]["message"]["content"]

def run_agent(user_query: str):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(run_agent_async(user_query))
    finally:
        loop.close()

def main():
    st.set_page_config(page_title="AI Трейдер (Finam)", page_icon="🤖", layout="wide")
    st.title("🤖 AI Ассистент Трейдера")
    st.caption("Интеллектуальный помощник для работы с Finam TradeAPI")
    with st.sidebar:
        st.header("⚙️ Настройки")
        settings = get_settings()
        st.info(f"**Модель:** {settings.openrouter_model}")
        with st.expander("🔑 Finam API", expanded=False):
            api_token = st.text_input("Access Token", type="password", help="Токен доступа к Finam TradeAPI (или используйте FINAM_ACCESS_TOKEN)")
            api_base_url = st.text_input("API Base URL", value="https://api.finam.ru", help="Базовый URL API")
        account_id = st.text_input("ID счета", value="", help="Оставьте пустым если не требуется")
        if st.button("🔄 Очистить историю"):
            st.session_state.messages = []
            st.rerun()
        st.markdown("---")
        st.markdown("### 💡 Примеры вопросов:")
        st.markdown("""
               - Какая цена Сбербанка?
               - Покажи мой портфель
               - Что в стакане по Газпрому?
               - Покажи свечи YNDX за последние дни
               - Какие у меня активные ордера?
               - Детали моей сессии
               """)
    if prompt := st.chat_input("Напишите ваш вопрос..."):
        with st.chat_message("assistant"), st.spinner("Думаю..."):
            try:
                response = run_agent(prompt)
                st.write(response)
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
