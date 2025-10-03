#!/usr/bin/env python3
"""
MrDom SDR AgentOS + Bedrock
Sistema de automação de vendas com agentes inteligentes
"""

import uvicorn
from src.mrdom.api import create_app
from src.mrdom.core.config import settings

def main():
    """Função principal da aplicação."""
    print("🚀 Iniciando MrDom SDR AgentOS + Bedrock...")
    print("=" * 50)
    
    # Cria aplicação
    app = create_app()
    
    # Configurações do servidor
    host = "0.0.0.0"
    port = 8000
    reload = settings.debug
    
    print(f"📱 Aplicação: {settings.app_name}")
    print(f"🔢 Versão: {settings.version}")
    print(f"🌍 Ambiente: {settings.environment}")
    print(f"🤖 Modelo: {settings.bedrock_model}")
    print(f"🌐 Servidor: http://{host}:{port}")
    print(f"📚 Documentação: http://{host}:{port}/docs")
    print(f"❤️ Health Check: http://{host}:{port}/api/v1/health")
    print(f"🤖 Status Agentes: http://{host}:{port}/api/v1/agents/status")
    print("=" * 50)
    
    # Inicia servidor
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
