"""
Configuração central do MrDom SDR AgentOS + Bedrock
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Aplicação
    app_name: str = "MrDom SDR AgentOS + Bedrock"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # AWS Bedrock
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field(default="us-east-1", env="AWS_DEFAULT_REGION")
    bedrock_model: str = Field(default="amazon.nova-lite-v1:0", env="BEDROCK_MODEL")
    
    # OpenAI (Fallback)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    
    # AgentOS
    agent_max_tokens: int = Field(default=1000, env="AGENT_MAX_TOKENS")
    agent_temperature: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    agentos_enabled: bool = Field(default=True, env="AGENTOS_ENABLED")
    
    # Chatwoot
    chatwoot_base_url: str = Field(default="https://app.chatwoot.com", env="CHATWOOT_BASE_URL")
    chatwoot_access_token: Optional[str] = Field(default=None, env="CHATWOOT_ACCESS_TOKEN")
    chatwoot_account_id: Optional[str] = Field(default=None, env="CHATWOOT_ACCOUNT_ID")
    chatwoot_hmac_secret: Optional[str] = Field(default=None, env="CHATWOOT_HMAC_SECRET")
    
    # N8N
    n8n_base_url: str = Field(default="http://localhost:5678", env="N8N_BASE_URL")
    n8n_api_key: Optional[str] = Field(default=None, env="N8N_API_KEY")
    
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/mrdom_sdr", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    metrics_endpoint: str = Field(default="/metrics", env="METRICS_ENDPOINT")
    
    # MrDom Specific
    bot_welcome_message: str = Field(
        default="Olá! 👋 Sou o Mr. DOM, assistente virtual da DOM360. Como posso ajudá-lo hoje?",
        env="BOT_WELCOME_MESSAGE"
    )
    escalation_keywords: List[str] = Field(
        default=["falar com humano", "atendente", "supervisor"],
        env="ESCALATION_KEYWORDS"
    )
    auto_response_enabled: bool = Field(default=True, env="AUTO_RESPONSE_ENABLED")
    business_hours: dict = Field(default={"start": "09:00", "end": "18:00"}, env="BUSINESS_HOURS")
    timezone: str = Field(default="America/Sao_Paulo", env="TIMEZONE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global das configurações
settings = Settings()
