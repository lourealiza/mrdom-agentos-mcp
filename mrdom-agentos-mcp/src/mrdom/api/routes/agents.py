"""
Rotas para agentes AgentOS + Bedrock
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from ...agents.bedrock_agent import BedrockAgent

router = APIRouter()

# Instância global do agente
bedrock_agent = BedrockAgent()

# Modelos Pydantic
class AgentProcessRequest(BaseModel):
    agent_type: str
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentProcessResponse(BaseModel):
    success: bool
    agent_type: str
    message: str
    response: Optional[str] = None
    context_used: Optional[bool] = None
    error: Optional[str] = None

class AgentSuggestionRequest(BaseModel):
    message: str

class AgentSuggestionResponse(BaseModel):
    message: str
    suggested_agent: str
    available_agents: List[str]

# Dependency para verificar se agentes estão disponíveis
async def check_agents_available():
    if not bedrock_agent.is_available():
        raise HTTPException(
            status_code=503, 
            detail="Agentes não estão disponíveis. Verifique configuração AWS Bedrock."
        )

@router.get("/status")
async def get_agents_status():
    """Status dos agentes AgentOS + Bedrock."""
    return {
        "agentos_available": bedrock_agent.is_available(),
        "model_provider": "AWS Bedrock",
        "model": "amazon.nova-lite-v1:0",
        "available_agents": bedrock_agent.get_available_agents(),
        "total_agents": len(bedrock_agent.get_available_agents())
    }

@router.get("/list")
async def list_agents(_: None = Depends(check_agents_available)):
    """Lista agentes disponíveis."""
    agents = bedrock_agent.get_available_agents()
    agent_descriptions = {
        "qualification": "Especialista em qualificação BANT",
        "sales": "SDR experiente em agendamento de demos",
        "support": "Especialista em suporte ao cliente"
    }
    
    return {
        "agents": [
            {
                "id": agent_id,
                "name": agent_id.title(),
                "description": agent_descriptions.get(agent_id, "Agente especializado")
            }
            for agent_id in agents
        ]
    }

@router.post("/process", response_model=AgentProcessResponse)
async def process_with_agent(
    request: AgentProcessRequest,
    _: None = Depends(check_agents_available)
):
    """Processa mensagem com agente específico."""
    try:
        result = await bedrock_agent.process_message(
            agent_type=request.agent_type,
            message=request.message,
            context=request.context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return AgentProcessResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-best")
async def process_with_best_agent(
    request: dict,
    _: None = Depends(check_agents_available)
):
    """Processa mensagem usando melhor agente automaticamente."""
    try:
        message = request.get("message", "")
        context = request.get("context", None)
        
        if not message:
            raise HTTPException(status_code=400, detail="Campo 'message' é obrigatório")
        
        result = await bedrock_agent.process_with_best_agent(message, context)
        
        return {
            "success": result["success"],
            "selected_agent": result.get("selected_agent"),
            "all_suggested_agents": result.get("all_suggested_agents", []),
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest", response_model=AgentSuggestionResponse)
async def suggest_agent(request: AgentSuggestionRequest):
    """Sugere melhor agente para mensagem."""
    try:
        suggested = bedrock_agent.suggest_agent(request.message)
        available = bedrock_agent.get_available_agents()
        
        return AgentSuggestionResponse(
            message=request.message,
            suggested_agent=suggested,
            available_agents=available
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
