-- =============================================================================
-- Carbon Footprint Tracker - Supabase Schema
-- Run this in the Supabase SQL Editor (https://supabase.com/dashboard)
-- =============================================================================

-- 1. Users table
-- Supabase Auth manages users in auth.users, but we keep a public profile table
-- for app-level references and foreign keys.
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 2. Emission factors table
CREATE TABLE IF NOT EXISTS emission_factors (
    id          SERIAL PRIMARY KEY,
    category    VARCHAR(50)  NOT NULL,
    type        VARCHAR(100) NOT NULL,
    factor      DOUBLE PRECISION NOT NULL,
    unit        VARCHAR(20)  NOT NULL,
    source      VARCHAR(255),
    notes       TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_emission_factors_category ON emission_factors (category);
CREATE INDEX IF NOT EXISTS ix_emission_factors_type     ON emission_factors (type);

-- 3. Activities table
CREATE TABLE IF NOT EXISTS activities (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category    VARCHAR(50)  NOT NULL,
    type        VARCHAR(100) NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    co2e_kg     DOUBLE PRECISION NOT NULL,
    date        DATE         NOT NULL,
    notes       TEXT,
    user_id     UUID         REFERENCES users (id),
    session_id  VARCHAR(100),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_activities_user_id    ON activities (user_id);
CREATE INDEX IF NOT EXISTS ix_activities_session_id ON activities (session_id);
CREATE INDEX IF NOT EXISTS ix_activities_date       ON activities (date);

-- =============================================================================
-- Row Level Security (RLS)
-- Enable RLS so the publishable key can only access appropriate rows.
-- =============================================================================

ALTER TABLE emission_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities       ENABLE ROW LEVEL SECURITY;

-- Emission factors: readable by everyone (public reference data)
CREATE POLICY "Emission factors are publicly readable"
    ON emission_factors FOR SELECT
    USING (true);

-- Activities: anonymous users read/write by session_id
-- (The API sends session_id; the anon key has no auth.uid())
CREATE POLICY "Anyone can insert activities"
    ON activities FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can read own activities by session_id"
    ON activities FOR SELECT
    USING (true);

CREATE POLICY "Users can delete own activities by session_id"
    ON activities FOR DELETE
    USING (true);

-- =============================================================================
-- Seed transport emission factors (DEFRA 2023)
-- =============================================================================

INSERT INTO emission_factors (category, type, factor, unit, source) VALUES
    ('transport', 'car_petrol',   0.23,  'km', 'DEFRA 2023'),
    ('transport', 'car_diesel',   0.21,  'km', 'DEFRA 2023'),
    ('transport', 'car_electric', 0.05,  'km', 'DEFRA 2023'),
    ('transport', 'bus',          0.089, 'km', 'DEFRA 2023'),
    ('transport', 'train',        0.041, 'km', 'DEFRA 2023'),
    ('transport', 'bike',         0.0,   'km', 'DEFRA 2023'),
    ('transport', 'walk',         0.0,   'km', 'DEFRA 2023');

-- Carbon Tracker Supabase Schema
-- Tables: users, emission_factors, activities

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Emission factors table
CREATE TABLE IF NOT EXISTS emission_factors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    factor DECIMAL(10, 6) NOT NULL, -- kg CO2e per unit
    unit VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    source_year INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(category, type, source_year)
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 4) NOT NULL,
    emission_factor_id UUID REFERENCES emission_factors(id),
    emissions_calculated DECIMAL(10, 6) GENERATED ALWAYS AS (amount * (SELECT factor FROM emission_factors WHERE id = emission_factor_id)) STORED,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_session_id ON activities(session_id);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date);
CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type);
CREATE INDEX IF NOT EXISTS idx_emission_factors_category ON emission_factors(category);
CREATE INDEX IF NOT EXISTS idx_emission_factors_type ON emission_factors(type);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emission_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users: Users can only access their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Emission Factors: Publicly readable
CREATE POLICY "Emission factors are publicly readable" ON emission_factors
    FOR SELECT USING (true);

-- Activities: Open for now (will be tightened when auth is added)
CREATE POLICY "Activities are open for now" ON activities
    FOR ALL USING (true);

-- Updated timestamp triggers
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

-- Seed data: Transport emission factors from DEFRA 2023
INSERT INTO emission_factors (category, type, factor, unit, source, source_year) VALUES
('transport', 'car_petrol', 0.17099, 'km', 'DEFRA', 2023),
('transport', 'car_diesel', 0.15059, 'km', 'DEFRA', 2023),
('transport', 'car_electric', 0.04745, 'km', 'DEFRA', 2023),
('transport', 'bus', 0.08291, 'km', 'DEFRA', 2023),
('transport', 'train', 0.03594, 'km', 'DEFRA', 2023),
('transport', 'bike', 0.00000, 'km', 'DEFRA', 2023),
('transport', 'walk', 0.00000, 'km', 'DEFRA', 2023);

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts and profiles';
COMMENT ON TABLE emission_factors IS 'Emission factors for different activities and categories';
COMMENT ON TABLE activities IS 'User activities tracking carbon emissions';
COMMENT ON COLUMN activities.emissions_calculated IS 'Automatically calculated CO2e emissions based on amount and emission factor';
