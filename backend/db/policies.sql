-- ==============================================================================
-- GramSehat Layer 7: Row Level Security (RLS) Policies
-- ==============================================================================
-- Security Architecture:
-- 1. All 7 tables have Row Level Security (RLS) enabled.
-- 2. The GramSehat backend uses the SUPABASE_SERVICE_KEY (service_role), which
--    bypasses RLS entirely for all CRUD operations.
-- 3. For the frontend client using SUPABASE_ANON_KEY (anon), read-only policies
--    are provided for demo realtime subscribers (prealerts and ambulance_requests),
--    as well as directory lookup for hospitals.
-- 4. In a production deployment, replace demo anon policies with granular
--    auth.uid() policies tied to patient ABHA / OTP identity and authenticated
--    clinician hospital staff roles.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Enable RLS on all 7 tables
-- ------------------------------------------------------------------------------
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE visits ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE prealerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambulance_requests ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------------------------
-- 2. Hospitals Table Policies
-- ------------------------------------------------------------------------------
-- Allow anon/authenticated public read access for hospital directory & locator
DROP POLICY IF EXISTS "Allow public read access on hospitals" ON hospitals;
CREATE POLICY "Allow public read access on hospitals"
ON hospitals
FOR SELECT
TO anon, authenticated
USING (true);

-- ------------------------------------------------------------------------------
-- 3. Prealerts Table Policies (Doctor Realtime Dashboard Demo)
-- ------------------------------------------------------------------------------
-- Allow read access for clinician ER terminal demo screen
DROP POLICY IF EXISTS "Allow anon read prealerts for demo dashboard" ON prealerts;
CREATE POLICY "Allow anon read prealerts for demo dashboard"
ON prealerts
FOR SELECT
TO anon, authenticated
USING (true);

-- ------------------------------------------------------------------------------
-- 4. Ambulance Requests Table Policies (Patient Tracking Realtime Demo)
-- ------------------------------------------------------------------------------
-- Allow read access for patient 108 ambulance tracking screen
DROP POLICY IF EXISTS "Allow anon read ambulance requests for demo tracking" ON ambulance_requests;
CREATE POLICY "Allow anon read ambulance requests for demo tracking"
ON ambulance_requests
FOR SELECT
TO anon, authenticated
USING (true);

-- ------------------------------------------------------------------------------
-- 5. Strict Default-Deny on Sensitive Patient Data
-- ------------------------------------------------------------------------------
-- patients, sessions, visits, and referrals have NO anon/authenticated policies.
-- Direct queries from the client anon key will return 0 rows (denied).
-- All writes and sensitive reads MUST flow through the backend using the service-role key.

-- ==============================================================================
-- PRODUCTION DEPLOYMENT GUIDANCE:
-- In production, replace the demo anon policies with authenticated role policies:
--
-- CREATE POLICY "Patients read own visits"
-- ON visits FOR SELECT TO authenticated
-- USING (auth.uid() = patient_id);
--
-- CREATE POLICY "Hospital staff read assigned prealerts"
-- ON prealerts FOR SELECT TO authenticated
-- USING (EXISTS (
--     SELECT 1 FROM hospital_staff
--     WHERE hospital_staff.user_id = auth.uid()
--       AND hospital_staff.hospital_id = prealerts.hospital_id
-- ));
-- ==============================================================================
