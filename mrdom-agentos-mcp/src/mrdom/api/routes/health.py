"""
Rotas de health check e monitoramento
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
import time
from datetime import datetime

from ...core.config import settings
from ...agents.bedrock_agent import BedrockAgent

router = APIRouter()

# Instância global do agente para health checks
bedrock_agent = BedrockAgent()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str
    uptime: float

class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str
    uptime: float
    components: Dict[str, Any]

# Variável para tracking de uptime
start_time = time.time()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check básico."""
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.version,
        environment=settings.environment,
        uptime=uptime
    )

@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Health check detalhado com componentes."""
    uptime = time.time() - start_time
    
    # Verifica componentes
    components = {
        "api": {"status": "healthy", "message": "API funcionando"},
        "bedrock_agent": {"status": "unknown", "message": "Não verificado"},
        "aws_credentials": {"status": "unknown", "message": "Não verificado"},
        "database": {"status": "unknown", "message": "Não verificado"},
        "redis": {"status": "unknown", "message": "Não verificado"}
    }
    
    # Verifica Bedrock Agent
    try:
        if bedrock_agent.is_available():
            components["bedrock_agent"] = {
                "status": "healthy",
                "message": f"Agentes disponíveis: {len(bedrock_agent.get_available_agents())}"
            }
        else:
            components["bedrock_agent"] = {
                "status": "unhealthy",
                "message": "Agentes não disponíveis"
            }
    except Exception as e:
        components["bedrock_agent"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Verifica AWS Credentials
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        components["aws_credentials"] = {
            "status": "healthy",
            "message": "Credenciais AWS configuradas"
        }
    else:
        components["aws_credentials"] = {
            "status": "unhealthy",
            "message": "Credenciais AWS não configuradas"
        }
    
    # Determina status geral
    overall_status = "healthy"
    for component, info in components.items():
        if info["status"] in ["unhealthy", "error"]:
            overall_status = "degraded"
            break
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        version=settings.version,
        environment=settings.environment,
        uptime=uptime,
        components=components
    )

@router.get("/ready")
async def readiness_check():
    """Readiness check para Kubernetes/Docker."""
    try:
        # Verifica se componentes críticos estão prontos
        if not bedrock_agent.is_available():
            raise HTTPException(status_code=503, detail="Agentes não disponíveis")
        
        if not settings.aws_access_key_id:
            raise HTTPException(status_code=503, detail="AWS credentials não configuradas")
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "message": "Sistema pronto para receber tráfego"
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/live")
async def liveness_check():
    """Liveness check para Kubernetes/Docker."""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - start_time
    }

@router.get("/metrics")
async def metrics():
    """Métricas básicas do sistema."""
    uptime = time.time() - start_time
    
    return {
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "version": settings.version,
        "environment": settings.environment,
        "agents": {
            "total": len(bedrock_agent.get_available_agents()),
            "available": bedrock_agent.get_available_agents()
        },
        "configuration": {
            "bedrock_model": settings.bedrock_model,
            "aws_region": settings.aws_default_region,
            "agentos_enabled": settings.agentos_enabled
        }
    }

@router.get("/info")
async def system_info():
    """Informações do sistema."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "Sistema de automação de vendas com agentes inteligentes usando AgentOS e AWS Bedrock",
        "author": "DOM-360",
        "repository": "https://github.com/DOM-360/mrdom-agentos-mcp",
        "documentation": "https://github.com/DOM-360/mrdom-agentos-mcp/docs",
        "environment": settings.environment,
        "debug": settings.debug,
        "features": [
            "AgentOS Integration",
            "AWS Bedrock Models",
            "N8N Workflow Integration",
            "Chatwoot Integration",
            "MrDom Qualification Logic",
            "Health Monitoring",
            "Prometheus Metrics"
        ]
    }
