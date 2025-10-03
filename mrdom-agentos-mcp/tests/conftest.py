"""
Configuração de testes para MrDom SDR AgentOS + Bedrock
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from src.mrdom.api import create_app
from src.mrdom.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def app():
    """Cria aplicação FastAPI para testes."""
    return create_app()

@pytest.fixture
def client(app):
    """Cria cliente de teste."""
    return TestClient(app)

@pytest.fixture
def mock_bedrock_agent():
    """Mock do BedrockAgent."""
    agent = Mock()
    agent.is_available.return_value = True
    agent.get_available_agents.return_value = ["qualification", "sales", "support"]
    agent.suggest_agent.return_value = "qualification"
    agent.process_with_best_agent = AsyncMock(return_value={
        "success": True,
        "response": "Resposta de teste",
        "selected_agent": "qualification"
    })
    return agent

@pytest.fixture
def mock_aws_credentials():
    """Mock das credenciais AWS."""
    return {
        "aws_access_key_id": "test_key",
        "aws_secret_access_key": "test_secret",
        "aws_default_region": "us-east-1"
    }

@pytest.fixture
def sample_conversation():
    """Dados de conversa de exemplo."""
    return {
        "id": "test-conversation-123",
        "platform": "chatwoot",
        "status": "active",
        "messages": [
            {
                "id": "msg-1",
                "content": "Olá, gostaria de saber mais sobre os planos",
                "message_type": "incoming",
                "sender": {"name": "João Silva", "email": "joao@empresa.com"}
            }
        ]
    }

@pytest.fixture
def sample_qualification_data():
    """Dados de qualificação de exemplo."""
    return {
        "lead_name": "João Silva",
        "company": "Empresa ABC",
        "email": "joao@empresa.com",
        "phone": "+55 11 99999-9999",
        "qualification_data": {
            "pos_nao_venda": "Sim, temos problemas",
            "integracao_mkt_vendas": "Não integrado",
            "ferramentas_atuais": "WhatsApp e email",
            "cta_agenda": "Sim, quero agendar",
            "confirmacao": "Confirmado",
            "follow_up": "Agendado para amanhã"
        },
        "status": "qualified"
    }
