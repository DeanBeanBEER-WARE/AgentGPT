from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from reworkd_platform.schemas.agent import ModelSettings
from reworkd_platform.web.api.agent.agent_service.agent_service import AgentService
from reworkd_platform.web.api.agent.agent_service.agent_service_provider import (
    get_agent_service,
)
from reworkd_platform.web.api.agent.analysis import Analysis
from reworkd_platform.web.api.agent.dependancies import agent_analyze_validator

router = APIRouter()

class TestRequest(BaseModel):
    goal: str
    task: str
    model_settings: Optional[ModelSettings] = None

@router.post("/test_analyze")
async def test_analyze(
    req_body: TestRequest,
    agent_service: AgentService = Depends(get_agent_service(agent_analyze_validator)),
) -> Analysis:
    """Test endpoint for analyzing tasks"""
    return await agent_service.analyze_task_agent(
        goal=req_body.goal,
        task=req_body.task,
        tool_names=["notion", "search"],  # Enable both tools for testing
    )
