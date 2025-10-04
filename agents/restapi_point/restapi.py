import uvicorn
from fastapi import FastAPI
from analyst import get_graph
from pydantic import BaseModel


class Inp(BaseModel):
    user_query: str
    account_id: str
service = FastAPI()

@service.on_event("startup")
async def startup():
    await get_graph()

@service.post("/process_data")
async def send_graph(input: Inp):
    graph_ = await get_graph()
    initial_state = {"messages": [{"role": "user", "content": input.user_query}], 'config': {"configurable": {"thread_id": input.account_id}}}

    result = await graph_.ainvoke(initial_state)
    return {"text": result['messages'][-1]['content']}

if __name__ == '__main__':
    uvicorn.run(service, port=8011)