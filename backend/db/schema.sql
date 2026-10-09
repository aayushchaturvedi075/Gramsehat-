-- ==============================================================================
-- GramSehat Layer 7: Database Schema (PostgreSQL / Supabase)
-- ==============================================================================
--
-- CANONICAL SPECIALTIES LIST:
-- 'cardiology', 'ophthalmology', 'obstetrics', 'pediatrics', 'neurology',
-- 'surgery', 'general_medicine', 'dermatology', 'emergency'
-- Use only these slug identifiers in hospitals.specialties.
--
-- Design Notes:
-- - All primary keys are UUIDs generated with gen_random_uuid().
-- - All timestamp columns use TIMESTAMPTZ defaulting to now().
-- - Check constraints enforce clinical triage tiers (red/yellow/green) and lifecycle states.
-- - GIN index on hospitals.specialties optimizes array containment queries.
-- ==============================================================================

-- Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. Patients Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    age NUMERIC,
    language TEXT DEFAULT 'hi',
    is_pregnant BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_patients_created_at ON patients (created_at DESC);

-- ------------------------------------------------------------------------------
-- 2. Sessions Table (Layer 6 conversational follow-up loop state)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE SET NULL,
    accumulated_text TEXT DEFAULT '',
    state JSONB DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sessions_patient_id ON sessions (patient_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions (status);

-- ------------------------------------------------------------------------------
-- 3. Visits Table (Triage records from Layer 2, Layer 4, and Layer 5)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    transcribed_text TEXT DEFAULT '',
    structured_symptoms JSONB DEFAULT '[]'::jsonb,
    screening_flags JSONB DEFAULT '[]'::jsonb,
    report_text TEXT DEFAULT '',
    urgency TEXT NOT NULL CHECK (urgency IN ('red', 'yellow', 'green')),
    triggered_rules TEXT[] DEFAULT '{}',
    reason TEXT DEFAULT '',
    required_specialty TEXT,
    recommended_action TEXT DEFAULT '',
    degraded BOOLEAN DEFAULT false,
    image_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_visits_patient_created ON visits (patient_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_visits_session_id ON visits (session_id);
CREATE INDEX IF NOT EXISTS idx_visits_urgency ON visits (urgency);
CREATE INDEX IF NOT EXISTS idx_visits_specialty ON visits (required_specialty);

-- ------------------------------------------------------------------------------
-- 4. Hospitals Table (Simulated referral network for rural demo)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- e.g. 'District Hospital', 'CHC', 'Eye Hospital', 'PHC'
    specialties TEXT[] NOT NULL DEFAULT '{}',
    beds_available INT NOT NULL DEFAULT 0 CHECK (beds_available >= 0),
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    contact TEXT,
    is_demo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_hospitals_specialties ON hospitals USING GIN (specialties);
CREATE INDEX IF NOT EXISTS idx_hospitals_beds ON hospitals (beds_available);
CREATE INDEX IF NOT EXISTS idx_hospitals_coords ON hospitals (lat, lng);

-- ------------------------------------------------------------------------------
-- 5. Referrals Table (Matches visit to selected hospital)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    hospital_id UUID REFERENCES hospitals(id) ON DELETE CASCADE,
    distance_km FLOAT NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_referrals_visit_id ON referrals (visit_id);
CREATE INDEX IF NOT EXISTS idx_referrals_hospital_id ON referrals (hospital_id);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON referrals (status);

-- ------------------------------------------------------------------------------
-- 6. Prealerts Table (Doctor pre-arrival notification - Realtime enabled)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prealerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID REFERENCES referrals(id) ON DELETE CASCADE,
    hospital_id UUID REFERENCES hospitals(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    urgency TEXT NOT NULL CHECK (urgency IN ('red', 'yellow', 'green')),
    eta_minutes INT DEFAULT 15 CHECK (eta_minutes >= 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'preparing', 'arrived', 'dismissed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_prealerts_referral_id ON prealerts (referral_id);
CREATE INDEX IF NOT EXISTS idx_prealerts_hospital_id ON prealerts (hospital_id);
CREATE INDEX IF NOT EXISTS idx_prealerts_created_at ON prealerts (created_at DESC);

-- ------------------------------------------------------------------------------
-- 7. Ambulance Requests Table (108 Dispatch & GPS tracking - Realtime enabled)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ambulance_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    hospital_id UUID REFERENCES hospitals(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'requested' CHECK (status IN ('requested', 'dispatched', 'in_transit', 'arrived', 'cancelled')),
    eta_minutes INT DEFAULT 15 CHECK (eta_minutes >= 0),
    vehicle_label TEXT DEFAULT 'Govt 108 Ambulance',
    current_lat FLOAT,
    current_lng FLOAT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ambulance_requests_visit_id ON ambulance_requests (visit_id);
CREATE INDEX IF NOT EXISTS idx_ambulance_requests_hospital_id ON ambulance_requests (hospital_id);
CREATE INDEX IF NOT EXISTS idx_ambulance_requests_status ON ambulance_requests (status);
