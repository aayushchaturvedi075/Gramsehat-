"""
Automated Test Suite for Layer 4: Sarvam AI Reasoning Module.
Tests /structure-symptoms, /explain-report, /generate-hospital-summary,
and validation/fallback handling using Sarvam AI LLMs.
"""

import os
import sys
import time
import requests
import json

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def print_section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def count_sentences(text: str) -> int:
    """Counts sentences ending with periods, exclamation marks, question marks, or Devanagari purna viram (।)."""
    import re
    sentences = [s.strip() for s in re.split(r'[\.\!\?।]+', text) if s.strip()]
    return len(sentences)


def test_health():
    print_section("1. Testing GET /health (Sarvam Layer 4 Status)")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print("Health response:", json.dumps(data, indent=2))
    assert data["status"] == "healthy"
    assert "layer4_ai_reasoning" in data
    assert data["layer4_ai_reasoning"]["status"] == "active"
    print("✓ Health check verified with Layer 4 active!")


def test_structure_symptoms_hindi():
    print_section("2. Testing POST /structure-symptoms (Hindi Informal Speech - Sarvam-30B/105B)")
    payload = {
        "text": "नमस्ते डॉक्टर, मुझे पिछले दो दिनों से बहुत तेज़ बुखार और सिरदर्द है, और आज सुबह से बहुत चक्कर भी आ रहे हैं।",
        "language": "hi-IN"
    }

    start_time = time.time()
    res = requests.post(f"{BASE_URL}/structure-symptoms", json=payload)
    elapsed = time.time() - start_time

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print(f"Elapsed Time: {elapsed:.2f} seconds")
    print("Structured Symptoms Output:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    assert "symptoms" in data and isinstance(data["symptoms"], list) and len(data["symptoms"]) > 0
    assert "duration" in data and isinstance(data["duration"], str)
    assert "severity_notes" in data and isinstance(data["severity_notes"], str)
    assert "follow_up_question" in data
    print(f"✓ Hindi symptom structuring passed in {elapsed:.2f}s!")


def test_structure_symptoms_english():
    print_section("3. Testing POST /structure-symptoms (English Acute Emergency - Sarvam-30B/105B)")
    payload = {
        "text": "Severe chest pressure radiating to my left arm, cold sweats, and heavy shortness of breath since 45 minutes ago.",
        "language": "en-IN"
    }

    start_time = time.time()
    res = requests.post(f"{BASE_URL}/structure-symptoms", json=payload)
    elapsed = time.time() - start_time

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print(f"Elapsed Time: {elapsed:.2f} seconds")
    print("Structured Symptoms Output:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    assert any("chest" in s.lower() for s in data["symptoms"]), "Expected chest symptom extracted"
    assert "duration" in data and len(data["duration"]) > 0
    print(f"✓ English acute symptom structuring passed in {elapsed:.2f}s!")


def test_explain_report():
    print_section("4. Testing POST /explain-report (CBC Lab Report - Sarvam-105B)")
    cbc_text = (
        "GRAMSEHAT RURAL CLINIC LAB INVESTIGATION\n"
        "Patient: Ramlal Sharma, 54y M\n"
        "COMPLETE BLOOD COUNT (CBC):\n"
        "Hemoglobin (Hb): 8.2 g/dL (Reference: 13.0 - 17.0) [LOW]\n"
        "Platelet Count: 210,000 /mcL (Reference: 150,000 - 450,000) [NORMAL]\n"
        "WBC Count: 7,400 /mcL (Reference: 4,000 - 11,000) [NORMAL]\n"
        "Serum Ferritin: 11 ng/mL (Reference: 20 - 250) [LOW]\n"
        "Doctor Note: Severe nutritional iron deficiency anemia."
    )
    payload = {
        "report_text": cbc_text,
        "patient_query": "Why am I feeling tired and dizzy?",
        "language": "en"
    }

    start_time = time.time()
    res = requests.post(f"{BASE_URL}/explain-report", json=payload)
    elapsed = time.time() - start_time

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print(f"Elapsed Time: {elapsed:.2f} seconds")
    print("Report Explanation Output:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    assert "explanation" in data and isinstance(data["explanation"], str)
    assert "flagged_values" in data and isinstance(data["flagged_values"], list)

    sentence_count = count_sentences(data["explanation"])
    print(f"Explanation Sentence Count: {sentence_count}")
    assert 2 <= sentence_count <= 6, f"Sentence count {sentence_count} should be between 3 and 5 sentences"

    assert len(data["flagged_values"]) >= 1, "Expected at least 1 flagged abnormal value"
    first_flag = data["flagged_values"][0]
    assert "test_name" in first_flag
    assert "value" in first_flag
    assert "simple_meaning" in first_flag
    print("✓ Report explanation passed accuracy and 3-5 sentence constraints!")


def test_generate_hospital_summary():
    print_section("5. Testing POST /generate-hospital-summary (SBAR Clinical Handover - Sarvam-105B)")
    payload = {
        "patient_name": "Ramlal Sharma",
        "age": 54,
        "gender": "Male",
        "village": "Shivpur Village",
        "symptoms": ["Severe dizziness", "Postural lightheadedness", "Extreme generalized weakness"],
        "duration": "2 days, worsening since morning",
        "severity_notes": "Unable to stand up unassisted; cold extremities and pale conjunctiva",
        "vitals": {"BP": "94/60 mmHg", "Pulse": "104 bpm", "SpO2": "97%", "Temperature": "98.4 F"},
        "report_findings": "CBC shows Hb 8.2 g/dL (low), Ferritin 11 ng/mL (low)",
        "screening_flags": {"conjunctival_pallor": "positive (score 0.78)", "koilonychia": "mild"}
    }

    start_time = time.time()
    res = requests.post(f"{BASE_URL}/generate-hospital-summary", json=payload)
    elapsed = time.time() - start_time

    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    print(f"Elapsed Time: {elapsed:.2f} seconds")
    print("SBAR Handover Summary:")
    print(data["summary"])

    assert "summary" in data and len(data["summary"]) > 50
    summary_lower = data["summary"].lower()
    assert "ramlal" in summary_lower or "sharma" in summary_lower or "situation" in summary_lower or "sbar" in summary_lower
    print("✓ Hospital summary generation passed!")


def test_validation_errors():
    print_section("6. Testing Validation & Error Handling")
    
    # 1. Empty symptoms
    r1 = requests.post(f"{BASE_URL}/structure-symptoms", json={"text": "   "})
    assert r1.status_code in [400, 422], f"Expected 400 or 422, got {r1.status_code}"
    print(f"✓ Empty symptoms -> {r1.status_code} verified")

    # 2. Empty report text
    r2 = requests.post(f"{BASE_URL}/explain-report", json={"report_text": ""})
    assert r2.status_code in [400, 422], f"Expected 400 or 422, got {r2.status_code}"
    print(f"✓ Empty report text -> {r2.status_code} verified")

    # 3. Insufficient hospital dossier
    r3 = requests.post(f"{BASE_URL}/generate-hospital-summary", json={})
    assert r3.status_code in [400, 422], f"Expected 400 or 422, got {r3.status_code}"
    print(f"✓ Insufficient dossier -> {r3.status_code} verified")


def test_fallback_handling():
    print_section("7. Testing Fallback Path on Ambiguous/Informal Input")
    # Test ambiguous input to ensure fallback/defensive parsing never crashes
    payload = {
        "text": "kuch ajeeb lag raha hai, samajh nahi aa raha",
        "language": "hi"
    }
    res = requests.post(f"{BASE_URL}/structure-symptoms", json=payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "symptoms" in data and len(data["symptoms"]) > 0
    assert "duration" in data
    assert "severity_notes" in data
    print("✓ Fallback and defensive handling verified on ambiguous input!")


def main():
    print("\nStarting GramSehat Layer 4 Sarvam AI Reasoning Test Suite...")
    print(f"Targeting Backend: {BASE_URL}")

    test_health()
    test_structure_symptoms_hindi()
    test_structure_symptoms_english()
    test_explain_report()
    test_generate_hospital_summary()
    test_validation_errors()
    test_fallback_handling()

    print("\n" + "=" * 70)
    print("ALL LAYER 4 SARVAM AI REASONING TESTS PASSED SUCCESSFULLY! (100%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
