from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from api.agent_service import initialize, post_message, project_client
from azure.ai.projects.models import Agent, AgentThread


router = APIRouter()


class MessageRequest(BaseModel):
    thread_id: str
    content: str

active_sessions: dict[str, tuple[Agent, AgentThread]] = {}


@router.post("/api/thread")
async def create_thread():
    try:
        async with project_client:
            agent, thread = await initialize()
            if not agent or not thread:
                raise HTTPException(status_code=500, detail="Initialization failed.")
            active_sessions[thread.id] = (agent, thread)
            return {"thread_id": thread.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/message")
async def send_message(req: MessageRequest):
    if req.thread_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Thread ID not found.")

    agent, thread = active_sessions[req.thread_id]

    try:
        response = await post_message(agent=agent, thread=thread, thread_id=req.thread_id, content=req.content)
        return {"agent": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")