-- ============================================================
-- Personal AI OS — Initial Schema Migration
-- Version: 001
-- Run this in Supabase SQL Editor after enabling pgvector
-- ============================================================

-- Enable pgvector (run this first if not already done)
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- SHARED LAYER
-- Readable by all managers via Admin
-- ============================================================

CREATE TABLE IF NOT EXISTS shared_identity (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    timezone        TEXT NOT NULL DEFAULT 'Europe/Berlin',
    languages       TEXT[] DEFAULT ARRAY['English'],
    home_city       TEXT,
    occupation      TEXT,
    communication_style     TEXT,
    preferred_alert_channel TEXT DEFAULT 'telegram_msg',
    wake_word       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shared_people (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name           TEXT NOT NULL,
    nickname            TEXT,
    relationship_type   TEXT CHECK (relationship_type IN ('friend', 'family', 'colleague', 'client', 'acquaintance')),
    importance_level    INTEGER CHECK (importance_level BETWEEN 1 AND 5),
    telegram_username   TEXT,
    email               TEXT,
    phone               TEXT,
    city                TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shared_preferences (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manager             TEXT NOT NULL,
    preference_key      TEXT NOT NULL,
    preference_value    TEXT NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (manager, preference_key)
);

-- ============================================================
-- ADMIN LAYER
-- ============================================================

CREATE TABLE IF NOT EXISTS admin_conversations (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id              TEXT NOT NULL,
    role                    TEXT CHECK (role IN ('user', 'assistant')),
    content                 TEXT NOT NULL,
    intent_classified       JSONB,
    managers_consulted      TEXT[],
    response_time_ms        INTEGER,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_delegation_log (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id         UUID REFERENCES admin_conversations(id) ON DELETE SET NULL,
    manager                 TEXT NOT NULL,
    task_sent               TEXT NOT NULL,
    response_received       JSONB,
    status                  TEXT CHECK (status IN ('success', 'partial', 'failed')) DEFAULT 'success',
    duration_ms             INTEGER,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_manager_health (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    manager             TEXT NOT NULL UNIQUE,
    last_seen_at        TIMESTAMPTZ,
    last_error          TEXT,
    error_count_24h     INTEGER DEFAULT 0,
    status              TEXT CHECK (status IN ('healthy', 'degraded', 'offline')) DEFAULT 'healthy',
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- LIFE ADMIN MANAGER
-- ============================================================

CREATE TABLE IF NOT EXISTS la_tasks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    description         TEXT,
    due_date            TIMESTAMPTZ,
    priority            TEXT CHECK (priority IN ('urgent', 'high', 'medium', 'low')) DEFAULT 'medium',
    category            TEXT CHECK (category IN ('assignment', 'personal', 'work', 'admin', 'other')) DEFAULT 'personal',
    status              TEXT CHECK (status IN ('pending', 'in_progress', 'done', 'overdue')) DEFAULT 'pending',
    notion_page_id      TEXT,
    reminder_sent_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS la_bills (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    amount_eur          NUMERIC(10, 2) NOT NULL,
    due_day_of_month    INTEGER CHECK (due_day_of_month BETWEEN 1 AND 31),
    payment_method      TEXT CHECK (payment_method IN ('direct_debit', 'manual', 'card')) DEFAULT 'manual',
    last_paid_at        TIMESTAMPTZ,
    next_due_at         TIMESTAMPTZ,
    status              TEXT CHECK (status IN ('paid', 'upcoming', 'overdue')) DEFAULT 'upcoming',
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS la_subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    TEXT NOT NULL,
    amount_eur              NUMERIC(10, 2) NOT NULL,
    billing_cycle           TEXT CHECK (billing_cycle IN ('monthly', 'yearly')) DEFAULT 'monthly',
    next_renewal_at         TIMESTAMPTZ,
    category                TEXT CHECK (category IN ('entertainment', 'tools', 'storage', 'education', 'other')) DEFAULT 'other',
    is_active               BOOLEAN DEFAULT TRUE,
    reminder_days_before    INTEGER DEFAULT 3,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS la_memory_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content         TEXT NOT NULL,
    embedding       vector(768),
    source_table    TEXT,
    source_id       UUID,
    manager         TEXT DEFAULT 'life_admin',
    importance      INTEGER CHECK (importance BETWEEN 1 AND 5) DEFAULT 3,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ
);

-- ============================================================
-- FINANCE MANAGER
-- ============================================================

CREATE TABLE IF NOT EXISTS fin_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date            DATE NOT NULL,
    description     TEXT NOT NULL,
    amount_eur      NUMERIC(10, 2) NOT NULL,
    type            TEXT CHECK (type IN ('income', 'expense', 'transfer')) NOT NULL,
    category        TEXT,
    subcategory     TEXT,
    source          TEXT CHECK (source IN ('bank_import', 'manual', 'auto_detected')) DEFAULT 'manual',
    is_anomalous    BOOLEAN DEFAULT FALSE,
    anomaly_note    TEXT,
    linked_bill_id  UUID REFERENCES la_bills(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fin_budgets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month           TEXT NOT NULL,
    category        TEXT NOT NULL,
    budgeted_eur    NUMERIC(10, 2) NOT NULL,
    spent_eur       NUMERIC(10, 2) DEFAULT 0,
    status          TEXT CHECK (status IN ('on_track', 'warning', 'exceeded')) DEFAULT 'on_track',
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (month, category)
);

CREATE TABLE IF NOT EXISTS fin_portfolio (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_name          TEXT NOT NULL,
    asset_type          TEXT CHECK (asset_type IN ('etf', 'stock', 'crypto', 'savings', 'other')),
    quantity            NUMERIC(18, 8) NOT NULL,
    avg_buy_price_eur   NUMERIC(10, 2),
    current_price_eur   NUMERIC(10, 2),
    current_value_eur   NUMERIC(10, 2),
    gain_loss_eur       NUMERIC(10, 2),
    gain_loss_pct       NUMERIC(8, 4),
    last_updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fin_memory_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content         TEXT NOT NULL,
    embedding       vector(768),
    source_table    TEXT,
    source_id       UUID,
    manager         TEXT DEFAULT 'finance',
    importance      INTEGER CHECK (importance BETWEEN 1 AND 5) DEFAULT 3,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ
);

-- ============================================================
-- CONTENT MANAGER
-- ============================================================

CREATE TABLE IF NOT EXISTS con_posts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform        TEXT CHECK (platform IN ('instagram', 'tiktok', 'youtube', 'linkedin')) NOT NULL,
    post_type       TEXT CHECK (post_type IN ('reel', 'photo', 'carousel', 'story', 'video')) NOT NULL,
    caption         TEXT,
    hashtags        TEXT[],
    posted_at       TIMESTAMPTZ,
    location_tag    TEXT,
    topic           TEXT,
    views           INTEGER DEFAULT 0,
    likes           INTEGER DEFAULT 0,
    comments        INTEGER DEFAULT 0,
    shares          INTEGER DEFAULT 0,
    saves           INTEGER DEFAULT 0,
    reach           INTEGER DEFAULT 0,
    engagement_rate NUMERIC(6, 4),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS con_ideas (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    description         TEXT,
    format              TEXT CHECK (format IN ('reel', 'photo', 'carousel', 'story', 'video')),
    topic               TEXT,
    inspiration_source  TEXT CHECK (inspiration_source IN ('trend', 'personal', 'client_request', 'research', 'other')) DEFAULT 'personal',
    status              TEXT CHECK (status IN ('idea', 'scripted', 'filmed', 'posted', 'archived')) DEFAULT 'idea',
    notion_page_id      TEXT,
    priority            TEXT CHECK (priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS con_analytics_summary (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period                      TEXT NOT NULL,
    platform                    TEXT NOT NULL,
    total_posts                 INTEGER DEFAULT 0,
    avg_engagement_rate         NUMERIC(6, 4),
    best_performing_post_id     UUID REFERENCES con_posts(id) ON DELETE SET NULL,
    best_performing_format      TEXT,
    best_performing_topic       TEXT,
    best_posting_time           TEXT,
    follower_count              INTEGER,
    follower_growth             INTEGER,
    notes                       TEXT,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (period, platform)
);

CREATE TABLE IF NOT EXISTS con_memory_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content         TEXT NOT NULL,
    embedding       vector(768),
    source_table    TEXT,
    source_id       UUID,
    manager         TEXT DEFAULT 'content',
    importance      INTEGER CHECK (importance BETWEEN 1 AND 5) DEFAULT 3,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ
);

-- ============================================================
-- RELATIONSHIPS MANAGER
-- ============================================================

CREATE TABLE IF NOT EXISTS rel_people (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shared_people_id            UUID REFERENCES shared_people(id) ON DELETE CASCADE,
    last_contacted_at           TIMESTAMPTZ,
    preferred_contact_method    TEXT CHECK (preferred_contact_method IN ('telegram', 'whatsapp', 'call', 'email', 'in_person')) DEFAULT 'telegram',
    contact_frequency_target    TEXT CHECK (contact_frequency_target IN ('weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')) DEFAULT 'monthly',
    relationship_health         TEXT CHECK (relationship_health IN ('close', 'drifting', 'reconnect', 'inactive')) DEFAULT 'close',
    my_notes                    TEXT,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rel_interactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id           UUID REFERENCES rel_people(id) ON DELETE CASCADE,
    interaction_type    TEXT CHECK (interaction_type IN ('text', 'call', 'met_in_person', 'email', 'social_media')) NOT NULL,
    date                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes               TEXT,
    initiated_by        TEXT CHECK (initiated_by IN ('me', 'them')) DEFAULT 'me',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rel_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id           UUID REFERENCES rel_people(id) ON DELETE CASCADE,
    event_type          TEXT CHECK (event_type IN ('birthday', 'anniversary', 'graduation', 'new_job', 'moved_city', 'custom')) NOT NULL,
    event_date          DATE NOT NULL,
    is_recurring        BOOLEAN DEFAULT FALSE,
    reminder_days_before INTEGER DEFAULT 3,
    last_reminded_at    TIMESTAMPTZ,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rel_memory_vectors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content         TEXT NOT NULL,
    embedding       vector(768),
    source_table    TEXT,
    source_id       UUID,
    manager         TEXT DEFAULT 'relationships',
    importance      INTEGER CHECK (importance BETWEEN 1 AND 5) DEFAULT 3,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ
);

-- ============================================================
-- SCHEDULED TASKS (Autonomous Scheduling — Phase 7)
-- ============================================================

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_description    TEXT NOT NULL,
    scheduled_for       TIMESTAMPTZ NOT NULL,
    assigned_manager    TEXT NOT NULL,
    status              TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'dead')) DEFAULT 'pending',
    retry_count         INTEGER DEFAULT 0,
    result              JSONB,
    error_log           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- Fast lookups on the most queried columns
-- ============================================================

-- Conversations
CREATE INDEX IF NOT EXISTS idx_admin_conversations_session ON admin_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_admin_conversations_created ON admin_conversations(created_at DESC);

-- Delegation log
CREATE INDEX IF NOT EXISTS idx_admin_delegation_manager ON admin_delegation_log(manager);
CREATE INDEX IF NOT EXISTS idx_admin_delegation_conversation ON admin_delegation_log(conversation_id);

-- Tasks
CREATE INDEX IF NOT EXISTS idx_la_tasks_status ON la_tasks(status);
CREATE INDEX IF NOT EXISTS idx_la_tasks_due_date ON la_tasks(due_date);

-- Bills & subscriptions
CREATE INDEX IF NOT EXISTS idx_la_bills_next_due ON la_bills(next_due_at);
CREATE INDEX IF NOT EXISTS idx_la_subscriptions_renewal ON la_subscriptions(next_renewal_at);
CREATE INDEX IF NOT EXISTS idx_la_subscriptions_active ON la_subscriptions(is_active);

-- Transactions
CREATE INDEX IF NOT EXISTS idx_fin_transactions_date ON fin_transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_fin_transactions_type ON fin_transactions(type);
CREATE INDEX IF NOT EXISTS idx_fin_transactions_anomalous ON fin_transactions(is_anomalous);

-- Posts
CREATE INDEX IF NOT EXISTS idx_con_posts_platform ON con_posts(platform);
CREATE INDEX IF NOT EXISTS idx_con_posts_posted_at ON con_posts(posted_at DESC);

-- Content ideas
CREATE INDEX IF NOT EXISTS idx_con_ideas_status ON con_ideas(status);

-- Relationships
CREATE INDEX IF NOT EXISTS idx_rel_people_shared ON rel_people(shared_people_id);
CREATE INDEX IF NOT EXISTS idx_rel_interactions_person ON rel_interactions(person_id);
CREATE INDEX IF NOT EXISTS idx_rel_events_date ON rel_events(event_date);
CREATE INDEX IF NOT EXISTS idx_rel_events_person ON rel_events(person_id);

-- Scheduled tasks
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_status ON scheduled_tasks(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_scheduled_for ON scheduled_tasks(scheduled_for);

-- Vector similarity search indexes (ivfflat — fast approximate search)
-- Note: only create these once you have data (100+ rows) — they need data to build properly
-- Run these separately after you have populated data:
-- CREATE INDEX ON la_memory_vectors   USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX ON fin_memory_vectors  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX ON con_memory_vectors  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX ON rel_memory_vectors  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================
-- SEED DATA
-- Your basic identity — update values to match you
-- ============================================================

INSERT INTO shared_identity (
    name,
    timezone,
    languages,
    home_city,
    occupation,
    communication_style,
    preferred_alert_channel,
    wake_word
) VALUES (
    'Sehaj',
    'Europe/Berlin',
    ARRAY['English', 'Hindi', 'Punjabi'],
    'Cologne',
    'Software Engineering Student + Python Backend Intern',
    'casual, concise, no fluff',
    'telegram_msg',
    'TBD'
) ON CONFLICT DO NOTHING;

-- Seed manager health rows so the admin knows about all managers from day one
INSERT INTO admin_manager_health (manager, status) VALUES
    ('life_admin',     'healthy'),
    ('finance',        'healthy'),
    ('content',        'healthy'),
    ('relationships',  'healthy')
ON CONFLICT (manager) DO NOTHING;

-- ============================================================
-- DONE
-- 25 tables created across 6 layers:
--   Shared (3), Admin (3), Life Admin (4),
--   Finance (4), Content (4), Relationships (4),
--   Scheduled Tasks (1) + vector tables (4)
-- ============================================================