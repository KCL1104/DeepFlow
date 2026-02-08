-- DeepFlow Database Schema
-- Run this SQL in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TASKS TABLE
-- Stores all tasks with AI-generated metadata
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Task Content
    title TEXT NOT NULL,
    summary TEXT,
    suggested_action TEXT,
    
    -- Priority & Scheduling
    urgency INTEGER DEFAULT 5 CHECK (urgency >= 0 AND urgency <= 10),
    estimated_minutes INTEGER,
    deadline TIMESTAMPTZ,
    
    -- Metadata
    context_tags TEXT[] DEFAULT '{}',
    source TEXT DEFAULT 'manual', -- manual, telegram, slack, email
    
    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'deferred')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Users can only access their own tasks
-- ============================================
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own tasks
CREATE POLICY "Users can view own tasks"
    ON tasks FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own tasks
CREATE POLICY "Users can insert own tasks"
    ON tasks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own tasks
CREATE POLICY "Users can update own tasks"
    ON tasks FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own tasks
CREATE POLICY "Users can delete own tasks"
    ON tasks FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- SERVICE ROLE BYPASS (for backend API)
-- ============================================
-- Allow service role to bypass RLS
CREATE POLICY "Service role has full access"
    ON tasks FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- UPDATED_AT TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- TELEGRAM USER BINDINGS (Optional)
-- Links Telegram user IDs to DeepFlow users
-- ============================================
CREATE TABLE IF NOT EXISTS telegram_bindings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL UNIQUE,
    telegram_username TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telegram_bindings_user_id ON telegram_bindings(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_bindings_telegram_id ON telegram_bindings(telegram_id);

-- RLS for telegram_bindings
ALTER TABLE telegram_bindings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own telegram bindings"
    ON telegram_bindings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own telegram bindings"
    ON telegram_bindings FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Service role has full access to telegram_bindings"
    ON telegram_bindings FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');
