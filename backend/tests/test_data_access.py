"""
Comprehensive Test Suite for GramSehat Layer 7: Data Access Layer
==================================================================
Tests:
- Patient creation & lookup
- Conversational session upsert & state tracking
- Visit persistence and chronological patient timeline (newest first)
- Layer 5 specialty string normalization to canonical slugs
- Hospital matching logic:
  * Specialty filter
  * Bed availability filter (skips 0-bed hospitals)
  * Haversine distance calculation and ascending ordering
  * Automatic fallback to emergency/general facilities (flagged fallback = true)
- Referral generation, doctor prealert creation, and ambulance GPS updates
- Document image upload and secure signed URL generation
- Strict DataError validation and zero credential logging
"""

import unittest
from app.services.data_access import (
    DataError,
    create_ambulance_request,
    create_prealert,
    find_hospitals,
    get_or_create_patient,
    get_session,
    get_signed_url,
    get_timeline,
    save_referral,
    save_visit,
    update_ambulance_position,
    upload_image,
    upsert_session,
)
from app.services.specialties import (
    CANONICAL_SPECIALTIES,
    CANONICAL_SPECIALTIES_SET,
    map_specialty_to_canonical,
)

# Reference center coordinate: Shivpur / Lucknow rural area
DEMO_LAT = 26.8467
DEMO_LNG = 80.9462


class TestDataAccessLayer(unittest.TestCase):
    """Test suite verifying persistence and data access contracts for Layer 7."""

    # --------------------------------------------------------------------------
    # 1. PATIENT MANAGEMENT
    # --------------------------------------------------------------------------

    def test_01_get_or_create_patient(self):
        """Creates a new patient and retrieves existing patient idempotently."""
        p1 = get_or_create_patient(
            name="Ramlal Sharma",
            age=54,
            language="hi",
            is_pregnant=False
        )
        self.assertIn("id", p1)
        self.assertEqual(p1["name"], "Ramlal Sharma")
        self.assertEqual(p1["age"], 54)
        self.assertEqual(p1["language"], "hi")
        self.assertFalse(p1["is_pregnant"])

        # Fetching the same patient name should return existing record
        p2 = get_or_create_patient(name="Ramlal Sharma")
        self.assertEqual(p1["id"], p2["id"])

    def test_02_empty_patient_name_raises_data_error(self):
        """Empty patient name must raise DataError."""
        with self.assertRaises(DataError):
            get_or_create_patient(name="")

    # --------------------------------------------------------------------------
    # 2. SESSION UPSERT & STATE MANAGEMENT
    # --------------------------------------------------------------------------

    def test_03_upsert_and_retrieve_session(self):
        """Tests session creation and progressive text/state accumulation."""
        p = get_or_create_patient(name="Kamla Devi", age=32)

        # 1. Initialize session
        s1 = upsert_session(
            session_id=None,
            patient_id=p["id"],
            accumulated_text="कल से चक्कर आ रहे हैं",
            state={"step": 1},
            status="active"
        )
        s_id = s1["id"]
        self.assertEqual(s1["status"], "active")
        self.assertIn("कल से चक्कर", s1["accumulated_text"])

        # 2. Update existing session
        s2 = upsert_session(
            session_id=s_id,
            patient_id=p["id"],
            accumulated_text="कल से चक्कर आ रहे हैं और उल्टी भी हुई",
            state={"step": 2, "clarification_asked": True},
            status="active"
        )
        self.assertEqual(s2["id"], s_id)
        self.assertIn("उल्टी भी हुई", s2["accumulated_text"])
        self.assertEqual(s2["state"]["step"], 2)

        # 3. Retrieve session by ID
        fetched = get_session(s_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], s_id)

    def test_04_invalid_session_status_raises_data_error(self):
        """Invalid session status must raise DataError."""
        with self.assertRaises(DataError):
            upsert_session(session_id=None, status="invalid_status")

    # --------------------------------------------------------------------------
    # 3. VISITS & PATIENT TIMELINE ORDERING
    # --------------------------------------------------------------------------

    def test_05_save_visit_and_get_timeline_newest_first(self):
        """Saves visits and verifies timeline returns them in newest-first order."""
        patient = get_or_create_patient(name="Suresh Verma", age=45)
        pid = patient["id"]

        # Visit 1 (Older)
        v1 = save_visit(
            patient_id=pid,
            session_id=None,
            transcribed_text="हल्का सिरदर्द",
            urgency="green",
            reason="हल्का सिरदर्द, कोई गंभीर लक्षण नहीं",
            required_specialty="General Medicine",
            recommended_action="आराम करें"
        )

        # Visit 2 (Newer - Emergency)
        v2 = save_visit(
            patient_id=pid,
            session_id=None,
            transcribed_text="सीने में तेज दर्द और सांस फूलना",
            structured_symptoms=["chest_pain", "breathlessness"],
            urgency="red",
            triggered_rules=["RED_CHEST_CARDIAC"],
            reason="Acute coronary risk",
            required_specialty="Cardiology",
            recommended_action="108 एम्बुलेंस से तुरंत कार्डियोलॉजी केंद्र जाएं"
        )

        timeline = get_timeline(patient_id=pid)
        self.assertTrue(len(timeline) >= 2)
        # Newest first: v2 must appear before v1
        self.assertEqual(timeline[0]["id"], v2["id"])
        self.assertEqual(timeline[0]["urgency"], "red")
        self.assertEqual(timeline[0]["required_specialty"], "cardiology")
        self.assertEqual(timeline[1]["id"], v1["id"])

    def test_06_invalid_visit_urgency_raises_data_error(self):
        """Invalid urgency tier must raise DataError."""
        p = get_or_create_patient(name="Test Patient")
        with self.assertRaises(DataError):
            save_visit(patient_id=p["id"], session_id=None, urgency="critical_emergency")

    # --------------------------------------------------------------------------
    # 4. CANONICAL SPECIALTIES MAPPING
    # --------------------------------------------------------------------------

    def test_07_specialty_mapping_all_layer5_outputs(self):
        """Verifies all Layer 5 clinical strings map to canonical slugs."""
        mappings = {
            "Cardiology": "cardiology",
            "Ophthalmology": "ophthalmology",
            "Obstetrics": "obstetrics",
            "Pediatrics": "pediatrics",
            "Emergency/Neurology": "neurology",
            "Emergency/Surgery": "surgery",
            "Emergency/General": "emergency",
            "General Medicine": "general_medicine",
            "General Medicine (blood test)": "general_medicine",
            "Dermatology": "dermatology",
            "skin": "dermatology",
            "Maternity": "obstetrics",
            "Heart": "cardiology",
        }

        for raw, expected in mappings.items():
            slug = map_specialty_to_canonical(raw)
            self.assertEqual(slug, expected, f"Failed mapping for '{raw}'")
            self.assertIn(slug, CANONICAL_SPECIALTIES_SET)

    # --------------------------------------------------------------------------
    # 5. HOSPITAL MATCHING, BED FILTERING & FALLBACK
    # --------------------------------------------------------------------------

    def test_08_match_hospitals_ophthalmology_skips_zero_beds(self):
        """Ophthalmology query matches Drishti Eye Institute and skips zero-bed clinic."""
        results = find_hospitals(specialty="Ophthalmology", lat=DEMO_LAT, lng=DEMO_LNG, limit=3)
        self.assertTrue(len(results) > 0)

        first_match = results[0]
        # Must return the hospital with available beds (>0)
        self.assertIn("Drishti Rural Eye Institute", first_match["name"])
        self.assertTrue(first_match["beds_available"] > 0)
        self.assertFalse(first_match["fallback"])
        self.assertTrue(first_match["distance_km"] > 0.0)

        # Ensure zero-bed clinic 'Avadh Netralaya' was not returned
        for h in results:
            self.assertNotEqual(h["name"], "Avadh Netralaya Vision Center (Demo)")
            self.assertTrue(h["beds_available"] > 0)

    def test_09_match_hospitals_cardiology_ordering(self):
        """Cardiology query returns Sanjivani Heart Institute with available beds."""
        results = find_hospitals(specialty="Cardiology", lat=DEMO_LAT, lng=DEMO_LNG, limit=3)
        self.assertTrue(len(results) > 0)

        first_match = results[0]
        self.assertIn("Sanjivani Heart", first_match["name"])
        self.assertEqual(first_match["beds_available"], 8)
        self.assertFalse(first_match["fallback"])
        self.assertTrue(isinstance(first_match["distance_km"], float))

    def test_10_match_hospitals_fallback_when_specialty_unavailable(self):
        """Unavailable specialty falls back to emergency or general medicine hospitals."""
        results = find_hospitals(specialty="NonExistentSpecialty123", lat=DEMO_LAT, lng=DEMO_LNG, limit=3)
        self.assertTrue(len(results) > 0)

        # Fallback flag must be True
        for h in results:
            self.assertTrue(h["fallback"])
            self.assertTrue(h["beds_available"] > 0)
            specs = h["specialties"]
            self.assertTrue("emergency" in specs or "general_medicine" in specs)

    def test_11_match_hospitals_distance_sorting(self):
        """Hospitals are returned sorted in strictly ascending order of distance."""
        results = find_hospitals(specialty="General Medicine", lat=DEMO_LAT, lng=DEMO_LNG, limit=5)
        self.assertTrue(len(results) >= 2)

        distances = [h["distance_km"] for h in results]
        self.assertEqual(distances, sorted(distances))

    # --------------------------------------------------------------------------
    # 6. REFERRAL, PREALERT & AMBULANCE DISPATCH
    # --------------------------------------------------------------------------

    def test_12_referral_and_prealert_creation(self):
        """Creates referral and hospital clinician prealert record."""
        p = get_or_create_patient(name="Meena Devi", is_pregnant=True)
        v = save_visit(patient_id=p["id"], urgency="red", required_specialty="Obstetrics")
        hospitals = find_hospitals(specialty="Obstetrics", lat=DEMO_LAT, lng=DEMO_LNG, limit=1)
        target_hospital = hospitals[0]

        referral = save_referral(
            visit_id=v["id"],
            hospital_id=target_hospital["id"],
            distance_km=target_hospital["distance_km"],
            status="pending"
        )
        self.assertIn("id", referral)
        self.assertEqual(referral["status"], "pending")

        prealert = create_prealert(
            referral_id=referral["id"],
            hospital_id=target_hospital["id"],
            summary="Emergency pre-eclampsia with visual symptoms, arriving in 18 min",
            urgency="red",
            eta_minutes=18
        )
        self.assertIn("id", prealert)
        self.assertEqual(prealert["urgency"], "red")
        self.assertEqual(prealert["eta_minutes"], 18)

    def test_13_ambulance_request_and_gps_telemetry_update(self):
        """Creates 108 ambulance dispatch and updates live coordinates and ETA."""
        p = get_or_create_patient(name="Mohan Lal")
        v = save_visit(patient_id=p["id"], urgency="red")
        hospitals = find_hospitals(specialty="Emergency", lat=DEMO_LAT, lng=DEMO_LNG, limit=1)
        hid = hospitals[0]["id"]

        amb = create_ambulance_request(
            visit_id=v["id"],
            hospital_id=hid,
            eta_minutes=15,
            vehicle_label="Govt 108 Ambulance #UP-32-E-1082",
            current_lat=DEMO_LAT + 0.005,
            current_lng=DEMO_LNG + 0.005
        )
        amb_id = amb["id"]
        self.assertEqual(amb["status"], "requested")
        self.assertEqual(amb["eta_minutes"], 15)

        # Update position in transit
        updated = update_ambulance_position(
            ambulance_request_id=amb_id,
            current_lat=DEMO_LAT + 0.010,
            current_lng=DEMO_LNG + 0.010,
            eta_minutes=8,
            status="in_transit"
        )
        self.assertEqual(updated["status"], "in_transit")
        self.assertEqual(updated["eta_minutes"], 8)
        self.assertEqual(updated["current_lat"], DEMO_LAT + 0.010)

    # --------------------------------------------------------------------------
    # 7. STORAGE: UPLOAD & SIGNED URLS
    # --------------------------------------------------------------------------

    def test_14_upload_image_and_generate_signed_url(self):
        """Uploads prescription image bytes and generates time-limited signed URL."""
        fake_image_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 200  # Mock JPEG bytes
        storage_path = upload_image(
            file_bytes=fake_image_bytes,
            filename="ramlal_prescription.jpg",
            content_type="image/jpeg"
        )
        self.assertTrue(storage_path.startswith("visits/"))
        self.assertIn("ramlal_prescription.jpg", storage_path)

        signed_url = get_signed_url(image_path=storage_path, expires_in=1800)
        self.assertIn(storage_path, signed_url)
        self.assertTrue(len(signed_url) > 20)


if __name__ == "__main__":
    unittest.main()
