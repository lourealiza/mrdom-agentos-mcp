#!/usr/bin/env python3
"""
Exemplo básico de uso do MrDom SDR AgentOS + Bedrock
"""

import asyncio
import os
from src.mrdom.agents.bedrock_agent import BedrockAgent
from src.mrdom.core.config import settings

async def main():
    """Exemplo básico de uso."""
    print("🤖 MrDom SDR AgentOS + Bedrock - Exemplo Básico")
    print("=" * 50)
    
    # Verifica configuração
    if not settings.aws_access_key_id:
        print("❌ AWS_ACCESS_KEY_ID não configurada")
        print("Configure no arquivo .env:")
        print("AWS_ACCESS_KEY_ID=sua_chave_aws")
        print("AWS_SECRET_ACCESS_KEY=seu_secret_aws")
        return
    
    try:
        # Cria agente
        agent = BedrockAgent()
        
        print("✅ Agente Bedrock criado com sucesso!")
        print(f"📋 Agentes disponíveis: {agent.get_available_agents()}")
        
        # Exemplos de uso
        test_cases = [
            {
                "message": "Quero saber mais sobre os planos do DOM360",
                "expected_agent": "qualification"
            },
            {
                "message": "Preciso agendar uma demo para amanhã",
                "expected_agent": "sales"
            },
            {
                "message": "Estou com problema na integração",
                "expected_agent": "support"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Teste {i}: {test_case['message']}")
            
            # Sugere agente
            suggested = agent.suggest_agent(test_case['message'])
            print(f"   Agente sugerido: {suggested}")
            
            # Processa mensagem
            result = await agent.process_with_best_agent(
                test_case['message'],
                {"test": True, "conversation_id": f"test_{i}"}
            )
            
            if result["success"]:
                print(f"   ✅ Resposta: {result['response'][:100]}...")
                print(f"   🤖 Agente usado: {result.get('selected_agent')}")
            else:
                print(f"   ❌ Erro: {result.get('error')}")
        
        print(f"\n🎉 Exemplo concluído!")
        print(f"\n📚 Próximos passos:")
        print(f"   1. Execute: python main.py")
        print(f"   2. Acesse: http://localhost:8000/docs")
        print(f"   3. Teste: curl http://localhost:8000/api/v1/agents/status")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print(f"\n🔧 Verifique:")
        print(f"   1. AWS credentials configuradas")
        print(f"   2. Região AWS correta")
        print(f"   3. Permissões Bedrock")

if __name__ == "__main__":
    asyncio.run(main())
