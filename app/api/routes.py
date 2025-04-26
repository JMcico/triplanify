from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from api.agent_service import (
    get_project_client, 
    initialize, 
    post_message, 
    get_agent,
    get_threads)
from azure.ai.projects.models import Agent, AgentThread


router = APIRouter()


class MessageRequest(BaseModel):
    thread_id: str
    content: str


@router.post("/api/thread")
async def create_thread():
    try:
        async with get_project_client() as project_client:
            agent, thread = await initialize()
            if not agent or not thread:
                raise HTTPException(status_code=500, detail="Initialization failed.")
            return {"thread_id": thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/message")
async def send_message(req: MessageRequest):
    try:
        async with get_project_client() as project_client:
            agent = await get_agent()
            thread = await get_threads(req.thread_id)

            response = await post_message(agent=agent, thread=thread, thread_id=req.thread_id, content=req.content)
            return {"agent": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")