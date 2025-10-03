-- MrDom SDR AgentOS + Bedrock Database Schema
-- PostgreSQL initialization script

-- Create database if not exists
CREATE DATABASE mrdom_sdr;

-- Connect to the database
\c mrdom_sdr;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create tables
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) UNIQUE,
    platform VARCHAR(50) NOT NULL, -- 'chatwoot', 'n8n', 'webhook'
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'incoming', 'outgoing', 'system'
    sender_info JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    input_text TEXT NOT NULL,
    output_text TEXT,
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qualifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    lead_name VARCHAR(255),
    company VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    qualification_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(50),
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversations_external_id ON conversations(external_id);
CREATE INDEX IF NOT EXISTS idx_conversations_platform ON conversations(platform);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_interactions_conversation_id ON agent_interactions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_agent_name ON agent_interactions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_created_at ON agent_interactions(created_at);

CREATE INDEX IF NOT EXISTS idx_qualifications_conversation_id ON qualifications(conversation_id);
CREATE INDEX IF NOT EXISTS idx_qualifications_status ON qualifications(status);
CREATE INDEX IF NOT EXISTS idx_qualifications_email ON qualifications(email);
CREATE INDEX IF NOT EXISTS idx_qualifications_created_at ON qualifications(created_at);

CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qualifications_updated_at BEFORE UPDATE ON qualifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, tags) VALUES
('system_startup', 1, 'count', '{"component": "database", "status": "initialized"}'),
('database_version', 15, 'version', '{"component": "postgresql"}');

-- Create views
CREATE OR REPLACE VIEW conversation_summary AS
SELECT 
    c.id,
    c.external_id,
    c.platform,
    c.status,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at,
    c.created_at,
    c.updated_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.external_id, c.platform, c.status, c.created_at, c.updated_at;

CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    agent_name,
    COUNT(*) as total_interactions,
    AVG(confidence_score) as avg_confidence,
    AVG(processing_time_ms) as avg_processing_time,
    COUNT(CASE WHEN confidence_score >= 0.8 THEN 1 END) as high_confidence_count,
    DATE_TRUNC('day', created_at) as date
FROM agent_interactions
GROUP BY agent_name, DATE_TRUNC('day', created_at)
ORDER BY date DESC, total_interactions DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE mrdom_sdr TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;
