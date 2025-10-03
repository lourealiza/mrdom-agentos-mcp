"""
Rotas para webhooks (Chatwoot, N8N, etc.)
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import hmac
import hashlib
import json

from ...core.config import settings
from ...agents.bedrock_agent import BedrockAgent

router = APIRouter()

# Instância global do agente
bedrock_agent = BedrockAgent()

class WebhookRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class WebhookResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    agent_used: Optional[str] = None
    error: Optional[str] = None

def verify_chatwoot_signature(request: Request) -> bool:
    """Verifica assinatura HMAC do Chatwoot."""
    if not settings.chatwoot_hmac_secret:
        return True  # Skip verification if no secret configured
    
    signature = request.headers.get("X-Chatwoot-Signature")
    if not signature:
        return False
    
    # Calcula HMAC do body
    body = request.body()
    expected_signature = hmac.new(
        settings.chatwoot_hmac_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/chatwoot", response_model=WebhookResponse)
async def chatwoot_webhook(request: Request):
    """Webhook do Chatwoot para processamento automático."""
    try:
        # Verifica assinatura se configurada
        if not verify_chatwoot_signature(request):
            raise HTTPException(status_code=401, detail="Assinatura inválida")
        
        # Parse do payload
        payload = await request.json()
        
        # Extrai dados da mensagem
        message_data = payload.get("message", {})
        conversation_data = payload.get("conversation", {})
        
        # Ignora mensagens outgoing (evita loop)
        if message_data.get("message_type") == "outgoing":
            return WebhookResponse(
                success=True,
                response="Mensagem outgoing ignorada",
                agent_used=None
            )
        
        # Extrai texto da mensagem
        message_text = message_data.get("content", "").strip()
        if not message_text:
            return WebhookResponse(
                success=True,
                response="Mensagem vazia ignorada",
                agent_used=None
            )
        
        # Prepara contexto
        context = {
            "conversation_id": conversation_data.get("id"),
            "account_id": conversation_data.get("account_id"),
            "contact_id": conversation_data.get("contact", {}).get("id"),
            "sender": message_data.get("sender", {}),
            "timestamp": message_data.get("created_at"),
            "source": "chatwoot"
        }
        
        # Processa com melhor agente
        result = await bedrock_agent.process_with_best_agent(message_text, context)
        
        if result["success"]:
            return WebhookResponse(
                success=True,
                response=result["response"],
                agent_used=result.get("selected_agent")
            )
        else:
            return WebhookResponse(
                success=False,
                error=result.get("error", "Erro desconhecido")
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/n8n", response_model=WebhookResponse)
async def n8n_webhook(request: Request):
    """Webhook do N8N para processamento de workflows."""
    try:
        # Parse do payload
        payload = await request.json()
        
        # Extrai dados
        message = payload.get("message", "")
        context = payload.get("context", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Campo 'message' é obrigatório")
        
        # Processa com melhor agente
        result = await bedrock_agent.process_with_best_agent(message, context)
        
        if result["success"]:
            return WebhookResponse(
                success=True,
                response=result["response"],
                agent_used=result.get("selected_agent")
            )
        else:
            return WebhookResponse(
                success=False,
                error=result.get("error", "Erro desconhecido")
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=WebhookResponse)
async def test_webhook(request: WebhookRequest):
    """Webhook de teste para validação."""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Campo 'message' é obrigatório")
        
        # Processa com melhor agente
        result = await bedrock_agent.process_with_best_agent(
            request.message, 
            request.context
        )
        
        if result["success"]:
            return WebhookResponse(
                success=True,
                response=result["response"],
                agent_used=result.get("selected_agent")
            )
        else:
            return WebhookResponse(
                success=False,
                error=result.get("error", "Erro desconhecido")
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chatwoot/status")
async def chatwoot_status():
    """Status da integração Chatwoot."""
    return {
        "enabled": bool(settings.chatwoot_access_token),
        "base_url": settings.chatwoot_base_url,
        "account_id": settings.chatwoot_account_id,
        "hmac_secret_configured": bool(settings.chatwoot_hmac_secret),
        "webhook_url": "/api/v1/webhooks/chatwoot"
    }

@router.get("/n8n/status")
async def n8n_status():
    """Status da integração N8N."""
    return {
        "enabled": bool(settings.n8n_api_key),
        "base_url": settings.n8n_base_url,
        "webhook_url": "/api/v1/webhooks/n8n"
    }
