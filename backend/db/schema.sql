-- Sentinel-AI 2.0 Database Schema
-- Original tables with additional columns for Cursor queries

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Teams table
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    company_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budgets table
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    team_id UUID REFERENCES teams(id),
    company_id UUID REFERENCES companies(id),
    budget_type VARCHAR(50) NOT NULL, -- 'user', 'team', 'company'
    amount DECIMAL(10,2) NOT NULL,
    spent DECIMAL(10,2) DEFAULT 0.0,
    period VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Provider configurations
CREATE TABLE provider_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    provider_type VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'groq', 'local'
    api_key VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Requests table (main table for AI requests)
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    team_id UUID REFERENCES teams(id),
    company_id UUID REFERENCES companies(id),
    prompt TEXT NOT NULL,
    response TEXT,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(255) NOT NULL,
    cost DECIMAL(10,6) NOT NULL,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    cache_hit BOOLEAN DEFAULT FALSE,
    cache_level VARCHAR(10), -- 'L1', 'L2', 'L3'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Additional columns for Cursor queries as specified in spec
    prompt_embedding VECTOR(384),
    cache_hit_level VARCHAR(10)
);

-- Cache entries table
CREATE TABLE cache_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_hash VARCHAR(64) UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(255) NOT NULL,
    cost DECIMAL(10,6) NOT NULL,
    cache_level VARCHAR(10) NOT NULL, -- 'L1', 'L2', 'L3'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Complexity analysis results
CREATE TABLE complexity_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES requests(id),
    prompt_hash VARCHAR(64) NOT NULL,
    complexity_score DECIMAL(3,2) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    factors JSONB NOT NULL, -- Store complexity factors
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metrics and analytics
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL, -- 'provider', 'cache', 'budget', 'complexity'
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    labels JSONB, -- Additional labels/metadata
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_team_id ON requests(team_id);
CREATE INDEX idx_requests_company_id ON requests(company_id);
CREATE INDEX idx_requests_created_at ON requests(created_at);
CREATE INDEX idx_requests_provider ON requests(provider);
CREATE INDEX idx_requests_cache_hit ON requests(cache_hit);

CREATE INDEX idx_cache_entries_prompt_hash ON cache_entries(prompt_hash);
CREATE INDEX idx_cache_entries_expires_at ON cache_entries(expires_at);
CREATE INDEX idx_cache_entries_cache_level ON cache_entries(cache_level);

CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_team_id ON budgets(team_id);
CREATE INDEX idx_budgets_company_id ON budgets(company_id);

CREATE INDEX idx_complexity_analysis_prompt_hash ON complexity_analysis(prompt_hash);
CREATE INDEX idx_complexity_analysis_score ON complexity_analysis(complexity_score);

CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX idx_metrics_type_name ON metrics(metric_type, metric_name);

-- Vector index for prompt embeddings (if using pgvector)
-- CREATE INDEX idx_requests_prompt_embedding ON requests USING ivfflat (prompt_embedding vector_cosine_ops);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_provider_configs_updated_at BEFORE UPDATE ON provider_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();