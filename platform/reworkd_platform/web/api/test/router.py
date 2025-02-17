from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from reworkd_platform.schemas.agent import ModelSettings
from reworkd_platform.web.api.agent.agent_service.agent_service import AgentService
from reworkd_platform.web.api.agent.agent_service.open_ai_agent_service import OpenAIAgentService
from reworkd_platform.web.api.agent.analysis import Analysis
from reworkd_platform.web.api.agent.model_factory import create_model
from reworkd_platform.services.tokenizer.token_service import TokenService

router = APIRouter(prefix="/test", tags=["test"])

class TestRequest(BaseModel):
    goal: str
    task: str
    model_settings: Optional[ModelSettings] = None

def get_test_agent_service() -> AgentService:
    """Get agent service without authentication"""
    model_settings = ModelSettings()  # Default settings
    model = create_model(model_settings)
    token_service = TokenService()
    return OpenAIAgentService(
        model=model,
        settings=model_settings,
        token_service=token_service,
        callbacks=None,
        user=None,
        oauth_crud=None,
    )

@router.post("/analyze")
async def test_analyze(
    req_body: TestRequest,
    agent_service: AgentService = Depends(get_test_agent_service),
) -> Analysis:
    """Test endpoint for analyzing tasks without authentication"""
    return await agent_service.analyze_task_agent(
        goal=req_body.goal,
        task=req_body.task,
        tool_names=["notion", "search"],  # Enable both tools for testing
    )
