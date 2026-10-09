-- ==============================================================================
-- GramSehat Layer 7: Hospital Seed Data (Demo Network)
-- ==============================================================================
-- 10 Fictional hospitals spread around a configurable demo coordinate.
-- All hospital names end in '(Demo)' and are flagged with is_demo = true.
--
-- Includes:
-- - 1 Ophthalmology hospital with beds (>0) and 1 with 0 beds (proves filter)
-- - 1 Maternity-capable District hospital (Obstetrics + Emergency)
-- - 1 Cardiac hospital with beds (>0) and 1 with 0 beds (proves filter)
-- - 2 General PHC / CHC facilities (General Medicine + Emergency)
-- - 1 Dedicated Pediatric facility (Pediatrics)
-- - 1 Neuro / Trauma surgery hospital (Neurology + Surgery + Emergency)
-- - 1 Dermatology clinic (Dermatology)
-- ==============================================================================

DO $$
DECLARE
    -- =========================================================================
    -- CONFIGURABLE DEMO REGION CENTER (Default: Shivpur / Lucknow Rural UP)
    -- Adjust these coordinates to re-center the simulated hospital cluster.
    -- =========================================================================
    c_lat FLOAT := 26.8467;
    c_lng FLOAT := 80.9462;
BEGIN
    -- Idempotent reset of demo hospital entries
    DELETE FROM hospitals WHERE is_demo = true;

    INSERT INTO hospitals (name, type, specialties, beds_available, lat, lng, contact, is_demo)
    VALUES
    -- 1. Eye Hospital (Ophthalmology with beds available)
    (
        'Drishti Rural Eye Institute (Demo)',
        'Eye Hospital',
        ARRAY['ophthalmology', 'general_medicine'],
        12,
        c_lat + 0.0210,
        c_lng + 0.0180,
        '+91 94150 11001',
        true
    ),

    -- 2. Eye Hospital with ZERO beds (Tests bed availability filter)
    (
        'Avadh Netralaya Vision Center (Demo)',
        'Eye Hospital',
        ARRAY['ophthalmology'],
        0,
        c_lat + 0.0090,
        c_lng - 0.0120,
        '+91 94150 11002',
        true
    ),

    -- 3. Maternity-Capable District Hospital (Obstetrics + Emergency)
    (
        'Rampur District Mother & Child Hospital (Demo)',
        'District Hospital',
        ARRAY['obstetrics', 'emergency', 'pediatrics', 'surgery'],
        24,
        c_lat - 0.0350,
        c_lng + 0.0410,
        '+91 94150 11003',
        true
    ),

    -- 4. Cardiac-Capable Care Center (Cardiology with beds available)
    (
        'Sanjivani Heart & Trauma Institute (Demo)',
        'Tertiary Care',
        ARRAY['cardiology', 'emergency', 'surgery'],
        8,
        c_lat + 0.0520,
        c_lng - 0.0310,
        '+91 94150 11004',
        true
    ),

    -- 5. Primary Health Centre (PHC)
    (
        'Shivpur Primary Health Centre (Demo)',
        'PHC',
        ARRAY['general_medicine', 'emergency'],
        6,
        c_lat + 0.0080,
        c_lng + 0.0060,
        '+91 94150 11005',
        true
    ),

    -- 6. Community Health Centre (CHC)
    (
        'Rampur Community Health Centre (Demo)',
        'CHC',
        ARRAY['general_medicine', 'emergency', 'surgery'],
        18,
        c_lat - 0.0180,
        c_lng + 0.0220,
        '+91 94150 11006',
        true
    ),

    -- 7. Dedicated Child Care Facility (Pediatrics)
    (
        'Bal Arogya Pediatric Centre (Demo)',
        'Child Care',
        ARRAY['pediatrics', 'emergency'],
        14,
        c_lat + 0.0150,
        c_lng - 0.0240,
        '+91 94150 11007',
        true
    ),

    -- 8. Cardiac Hospital with ZERO beds (Tests bed availability filter)
    (
        'Gomti Rural Cardiac Annex (Demo)',
        'Specialty Clinic',
        ARRAY['cardiology'],
        0,
        c_lat + 0.0120,
        c_lng + 0.0350,
        '+91 94150 11008',
        true
    ),

    -- 9. Neuro & Multi-Trauma Emergency Hospital (Neurology + Emergency)
    (
        'Mahamaya Neuro & Trauma Hospital (Demo)',
        'Trauma Centre',
        ARRAY['neurology', 'surgery', 'emergency'],
        10,
        c_lat - 0.0420,
        c_lng - 0.0290,
        '+91 94150 11009',
        true
    ),

    -- 10. Dermatology & Skin Health Clinic
    (
        'Kalyan Skin & General Wellness Clinic (Demo)',
        'Clinic',
        ARRAY['dermatology', 'general_medicine'],
        4,
        c_lat + 0.0320,
        c_lng + 0.0150,
        '+91 94150 11010',
        true
    );

    RAISE NOTICE 'Successfully seeded 10 demo hospitals around lat=%, lng=%', c_lat, c_lng;
END $$;
