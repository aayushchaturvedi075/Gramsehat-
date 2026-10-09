-- ==============================================================================
-- GramSehat Layer 7: Supabase Realtime & Storage Setup
-- ==============================================================================
-- 1. Adds 'prealerts' and 'ambulance_requests' to the supabase_realtime publication
--    enabling live subscriptions on hospital ER dashboards & patient ambulance tracking.
-- 2. Creates the private 'patient-images' storage bucket for medical report photos.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Enable Supabase Realtime
-- ------------------------------------------------------------------------------
-- Ensure full replica identity so old & new row states are broadcast on updates
ALTER TABLE prealerts REPLICA IDENTITY FULL;
ALTER TABLE ambulance_requests REPLICA IDENTITY FULL;

DO $$
BEGIN
    -- Enable Realtime on prealerts
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime' AND tablename = 'prealerts'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE prealerts;
        RAISE NOTICE 'Added prealerts to supabase_realtime publication.';
    END IF;

    -- Enable Realtime on ambulance_requests
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime' AND tablename = 'ambulance_requests'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE ambulance_requests;
        RAISE NOTICE 'Added ambulance_requests to supabase_realtime publication.';
    END IF;
END $$;

-- ------------------------------------------------------------------------------
-- 2. Storage Setup: 'patient-images' Private Bucket
-- ------------------------------------------------------------------------------
-- Private bucket: objects cannot be viewed without signed URLs or service-role auth.
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'patient-images',
    'patient-images',
    false,
    15728640,  -- 15 MB maximum per image
    ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE SET
    public = false,
    file_size_limit = 15728640,
    allowed_mime_types = ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

-- Storage Access Policies:
-- Backend uses service_role key to upload and generate signed URLs (bypasses RLS).
-- Allow authenticated or service role full storage management:
DO $$
BEGIN
    DROP POLICY IF EXISTS "Allow service role full access on patient-images" ON storage.objects;
    CREATE POLICY "Allow service role full access on patient-images"
    ON storage.objects
    FOR ALL
    TO service_role
    USING (bucket_id = 'patient-images')
    WITH CHECK (bucket_id = 'patient-images');
EXCEPTION
    WHEN undefined_table THEN
        NULL;
END $$;

-- Note on Signed URLs:
-- Time-limited signed URLs are generated via the Python data access layer:
--   supabase.storage.from_('patient-images').create_signed_url(path, expires_in=3600)
-- The resulting signed URL provides secure, temporary GET access for clinician viewing.
