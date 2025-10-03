"""
API MrDom SDR AgentOS + Bedrock
"""

from fastapi import FastAPI
from .routes import agents, health, webhooks
from ..core.config import settings


def create_app() -> FastAPI:
    """Cria aplicação FastAPI."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Sistema de automação de vendas com agentes inteligentes usando AgentOS e AWS Bedrock",
        debug=settings.debug
    )
    
    # Inclui rotas
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
    
    return app
