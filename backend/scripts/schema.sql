-- =============================================================================
-- Carbon Footprint Tracker - Database Schema
-- Run this in the Supabase SQL Editor or against a local PostgreSQL database.
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users table
-- Supabase Auth manages users in auth.users, but we keep a public profile table
-- for app-level references and foreign keys.
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Emission factors table
CREATE TABLE IF NOT EXISTS emission_factors (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category    VARCHAR(100) NOT NULL,
    type        VARCHAR(100) NOT NULL,
    factor      DECIMAL(10, 6) NOT NULL, -- kg CO2e per unit
    unit        VARCHAR(50)  NOT NULL,
    source      VARCHAR(100) NOT NULL,
    source_year INTEGER      NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(category, type, source_year)
);

-- 3. Activities table
CREATE TABLE IF NOT EXISTS activities (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id  VARCHAR(255),
    category    VARCHAR(100) NOT NULL,
    type        VARCHAR(100) NOT NULL,
    value       DECIMAL(10, 4) NOT NULL,
    co2e_kg     DECIMAL(10, 6) NOT NULL,
    date        DATE         NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_session_id ON activities(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date);
CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type);
CREATE INDEX IF NOT EXISTS idx_emission_factors_category ON emission_factors(category);
CREATE INDEX IF NOT EXISTS idx_emission_factors_type ON emission_factors(type);

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emission_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

-- Emission factors: readable by everyone (public reference data)
CREATE POLICY "Emission factors are publicly readable"
    ON emission_factors FOR SELECT
    USING (true);

-- Emission factors: can be inserted by anyone (for seeding)
CREATE POLICY "Anyone can insert emission factors"
    ON emission_factors FOR INSERT
    WITH CHECK (true);

-- Activities: open for now (will be tightened when auth is added)
CREATE POLICY "Anyone can insert activities"
    ON activities FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Anyone can read activities"
    ON activities FOR SELECT
    USING (true);

CREATE POLICY "Anyone can delete activities"
    ON activities FOR DELETE
    USING (true);

-- Users: users can only access their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- =============================================================================
-- Updated timestamp triggers
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emission_factors_updated_at BEFORE UPDATE ON emission_factors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Documentation
-- =============================================================================
COMMENT ON TABLE users IS 'User accounts and profiles';
COMMENT ON TABLE emission_factors IS 'Emission factors for different activities and categories';
COMMENT ON TABLE activities IS 'User activities tracking carbon emissions';
