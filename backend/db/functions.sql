-- ==============================================================================
-- GramSehat Layer 7: Hospital Matching SQL Function (match_hospitals)
-- ==============================================================================
-- Matches nearest hospital with available beds and requested specialty.
-- If no hospital matches with beds > 0, falls back to the nearest emergency
-- or general_medicine hospital with available beds (flagged fallback = true).
--
-- Distance calculation uses the Haversine spherical formula (Earth radius: 6371 km).
-- ==============================================================================

CREATE OR REPLACE FUNCTION match_hospitals(
    p_specialty TEXT,
    p_lat FLOAT,
    p_lng FLOAT,
    p_limit INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    specialties TEXT[],
    beds_available INT,
    lat FLOAT,
    lng FLOAT,
    contact TEXT,
    distance_km FLOAT,
    fallback BOOLEAN
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_match_count INT := 0;
BEGIN
    -- 1. Check count of primary matches with available beds
    SELECT COUNT(*)
    INTO v_match_count
    FROM hospitals h
    WHERE (p_specialty = ANY(h.specialties))
      AND h.beds_available > 0;

    -- 2. If primary specialty with beds > 0 is found, return nearest matching hospitals
    IF v_match_count > 0 THEN
        RETURN QUERY
        SELECT 
            h.id,
            h.name,
            h.type,
            h.specialties,
            h.beds_available,
            h.lat,
            h.lng,
            h.contact,
            ROUND(
                (2 * 6371 * asin(
                    sqrt(
                        power(sin(radians(h.lat - p_lat) / 2), 2) +
                        cos(radians(p_lat)) * cos(radians(h.lat)) * power(sin(radians(h.lng - p_lng) / 2), 2)
                    )
                ))::numeric,
                2
            )::FLOAT AS distance_km,
            false AS fallback
        FROM hospitals h
        WHERE (p_specialty = ANY(h.specialties))
          AND h.beds_available > 0
        ORDER BY distance_km ASC
        LIMIT p_limit;

    -- 3. Fallback: return nearest hospitals offering emergency or general_medicine
    ELSE
        RETURN QUERY
        SELECT 
            h.id,
            h.name,
            h.type,
            h.specialties,
            h.beds_available,
            h.lat,
            h.lng,
            h.contact,
            ROUND(
                (2 * 6371 * asin(
                    sqrt(
                        power(sin(radians(h.lat - p_lat) / 2), 2) +
                        cos(radians(p_lat)) * cos(radians(h.lat)) * power(sin(radians(h.lng - p_lng) / 2), 2)
                    )
                ))::numeric,
                2
            )::FLOAT AS distance_km,
            true AS fallback
        FROM hospitals h
        WHERE ('emergency' = ANY(h.specialties) OR 'general_medicine' = ANY(h.specialties))
          AND h.beds_available > 0
        ORDER BY distance_km ASC
        LIMIT p_limit;
    END IF;

    RETURN;
END;
$$;
