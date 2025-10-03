"""
Agente base usando AWS Bedrock
"""

import os
import asyncio
from typing import Dict, Any, Optional
from agno.agent import Agent
from agno.models.aws_bedrock import BedrockChat
from agno.os import AgentOS

from ..core.config import settings


class BedrockAgent:
    """Agente base usando AWS Bedrock."""
    
    def __init__(self):
        self.agent_os = None
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa agentes com Bedrock."""
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            raise ValueError("AWS credentials não configuradas")
        
        # Agente de Qualificação
        self.agents["qualification"] = Agent(
            id="mrdom-qualification",
            model=BedrockChat(
                id=settings.bedrock_model,
                sistema_prompt="""Você é Mr. DOM, especialista em qualificação de leads BANT 
                (Budget, Authority, Need, Timeline) da DOM360. 
                
                Sua missão é:
                1. Fazer perguntas inteligentes para qualificar leads
                2. Identificar necessidades e urgências
                3. Determinar fit comercial
                4. Coletar dados essenciais
                
                Seja consultivo, direto e cordial. Foque em valor, não em produto."""
            )
        )
        
        # Agente de Vendas
        self.agents["sales"] = Agent(
            id="mrdom-sales",
            model=BedrockChat(
                id=settings.bedrock_model,
                sistema_prompt="""Você é Mr. DOM, SDR experiente da DOM360.
                
                Sua missão é:
                1. Gerar interesse em demos
                2. Agendar reuniões de vendas
                3. Criar urgência para decisão
                4. Confirmar dados para contato
                
                Use técnicas de vendas consultivas. Seja persuasivo mas respeitoso."""
            )
        )
        
        # Agente de Suporte
        self.agents["support"] = Agent(
            id="mrdom-support",
            model=BedrockChat(
                id=settings.bedrock_model,
                sistema_prompt="""Você é Mr. DOM, especialista em sucesso do cliente da DOM360.
                
                Sua missão é:
                1. Resolver problemas rapidamente
                2. Explicar soluções claramente
                3. Identificar oportunidades de melhoria
                4. Escalar quando necessário
                
                Priorize satisfação do cliente e resolução eficiente."""
            )
        )
    
    async def process_message(self, agent_type: str, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Processa mensagem com agente específico."""
        if agent_type not in self.agents:
            return {
                "success": False,
                "error": f"Tipo de agente '{agent_type}' não encontrado"
            }
        
        try:
            agent = self.agents[agent_type]
            
            # Prepara contexto
            context_str = ""
            if context:
                context_str = f"\nContexto: {context}"
            
            # Processa mensagem
            response = await agent.arun(f"{message}{context_str}")
            
            return {
                "success": True,
                "agent_type": agent_type,
                "response": response.content,
                "context_used": context is not None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type
            }
    
    def suggest_agent(self, message: str) -> str:
        """Sugere melhor agente baseado na mensagem."""
        message_lower = message.lower()
        
        # Palavras-chave para qualificação
        if any(word in message_lower for word in ["preço", "custo", "orçamento", "investimento", "quanto"]):
            return "qualification"
        
        # Palavras-chave para vendas
        elif any(word in message_lower for word in ["demo", "reunião", "agendar", "apresentação", "meeting"]):
            return "sales"
        
        # Palavras-chave para suporte
        elif any(word in message_lower for word in ["problema", "bug", "erro", "suporte", "ajuda", "não funciona"]):
            return "support"
        
        # Default para qualificação
        else:
            return "qualification"
    
    async def process_with_best_agent(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Processa mensagem usando melhor agente automaticamente."""
        best_agent = self.suggest_agent(message)
        result = await self.process_message(best_agent, message, context)
        
        return {
            **result,
            "selected_agent": best_agent,
            "all_suggested_agents": [best_agent]
        }
    
    def get_available_agents(self) -> list:
        """Retorna lista de agentes disponíveis."""
        return list(self.agents.keys())
    
    def is_available(self) -> bool:
        """Verifica se agentes estão disponíveis."""
        return len(self.agents) > 0
