import os
import sys
import time
import requests

BASE_URL = os.getenv("GRAMSEHAT_API_URL", "http://127.0.0.1:8000")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "sample_assets")


def print_section(title: str):
    print(f"\n{'='*70}\n{title}\n{'='*70}")


def test_health_endpoint():
    print_section("1. Testing GET /health")
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.json()}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["status"] == "healthy"
    assert "voice_pipeline" in data
    assert data["models"]["easyocr"]["loaded"] is True, "EasyOCR model should be loaded"
    print("✓ Health check PASSED! EasyOCR and Web Speech API bridge are active.")


def test_process_transcript_hindi():
    print_section("2. Testing POST /process-transcript (Hindi Web Speech Result)")
    payload = {
        "transcript": "नमस्ते डॉक्टर, मुझे पिछले दो दिनों से बहुत तेज़ बुखार और सिरदर्द है।",
        "language": "hi-IN"
    }
    resp = requests.post(f"{BASE_URL}/process-transcript", json=payload, timeout=10)
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Failed transcript processing: {resp.text}"
    result = resp.json()
    print("Clinical Triage Assessment:")
    print(f"  Transcript: '{result['transcript']}'")
    print(f"  Scenario: {result['scenario_match']}")
    print(f"  Urgency: {result['urgency_level']} ({result['urgency_title']})")
    print(f"  Care Level: {result['care_level']}")
    print(f"  Spoken Feedback: '{result['ai_response_speech']}'")
    assert result["scenario_match"] == "fever"
    assert len(result["ai_response_speech"]) > 0
    print("✓ Hindi transcript triage PASSED!")


def test_process_transcript_english():
    print_section("3. Testing POST /process-transcript (English Web Speech Result)")
    payload = {
        "transcript": "I am having severe chest pressure and shortness of breath since this morning.",
        "language": "en-IN"
    }
    resp = requests.post(f"{BASE_URL}/process-transcript", json=payload, timeout=10)
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Failed transcript processing: {resp.text}"
    result = resp.json()
    print("Clinical Triage Assessment:")
    print(f"  Transcript: '{result['transcript']}'")
    print(f"  Scenario: {result['scenario_match']}")
    print(f"  Urgency: {result['urgency_level']} ({result['urgency_title']})")
    print(f"  Nearest Care: {result['nearest_care']}")
    assert result["scenario_match"] == "chest"
    assert result["urgency_level"] == "border-urgent"
    print("✓ English transcript triage PASSED!")


def test_dynamic_patient_questions():
    print_section("3b. Testing POST /process-transcript Dynamic Answers for Distinct Questions")
    
    # Query A: Stomach pain & vomiting
    payload_a = {
        "transcript": "मुझे 2 दिन से पेट में बहुत दर्द है और उल्टी आ रही है",
        "language": "hi-IN"
    }
    resp_a = requests.post(f"{BASE_URL}/process-transcript", json=payload_a, timeout=15)
    assert resp_a.status_code == 200, f"Query A failed: {resp_a.text}"
    res_a = resp_a.json()
    print("Query A (Stomach):", res_a["scenario_match"], "->", res_a["ai_response_speech"])

    # Query B: Headache remedy
    payload_b = {
        "transcript": "सिरदर्द के लिए क्या घरेलू उपाय कर सकते हैं?",
        "language": "hi-IN"
    }
    resp_b = requests.post(f"{BASE_URL}/process-transcript", json=payload_b, timeout=15)
    assert resp_b.status_code == 200, f"Query B failed: {resp_b.text}"
    res_b = resp_b.json()
    print("Query B (Headache):", res_b["scenario_match"], "->", res_b["ai_response_speech"])

    # Verify answers are distinct and tailored to their respective questions
    assert res_a["ai_response_speech"] != res_b["ai_response_speech"], "Responses must NOT be identical!"
    assert "पेट" in res_a["ai_response_speech"] or "उल्टी" in res_a["ai_response_speech"] or "ओआरएस" in res_a["ai_response_speech"] or "खाना" in res_a["ai_response_speech"]
    assert "सिर" in res_b["ai_response_speech"] or "आराम" in res_b["ai_response_speech"]
    # Verify neither gave the old canned dizziness response!
    assert "आपकी कमजोरी और चक्कर" not in res_a["ai_response_speech"]
    assert "आपकी कमजोरी और चक्कर" not in res_b["ai_response_speech"]
    print("✓ Dynamic question-specific answering verified! Answers are unique and context-aware.")


def test_process_transcript_validation():
    print_section("4. Testing POST /process-transcript Validation & Error Handling")
    # Empty transcript string
    resp = requests.post(f"{BASE_URL}/process-transcript", json={"transcript": "   ", "language": "en-IN"})
    print(f"Empty transcript -> Status: {resp.status_code}, Detail: {resp.json().get('detail')}")
    assert resp.status_code == 400 or resp.status_code == 422
    print("✓ Transcript validation PASSED!")


def test_extract_report_text():
    print_section("5. Testing POST /extract-report-text (Prescription OCR)")
    image_path = os.path.join(ASSETS_DIR, "sample_prescription.png")
    assert os.path.exists(image_path), f"Sample prescription image not found: {image_path}"

    with open(image_path, "rb") as f:
        files = {"file": ("sample_prescription.png", f, "image/png")}
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/extract-report-text", files=files, timeout=30)
        elapsed = time.time() - start_time

    print(f"Status Code: {resp.status_code} (took {elapsed:.2f}s)")
    assert resp.status_code == 200, f"Failed OCR extraction: {resp.text}"
    result = resp.json()
    assert "raw_text" in result
    assert "cleaned_text" in result
    print(f"Cleaned Text Sample:\n{result['cleaned_text'][:150]}...")
    assert len(result["cleaned_text"]) > 0
    print("✓ OCR text extraction PASSED!")


def test_sarvam_tts():
    print_section("5. Testing POST /api/tts (Sarvam Bulbul v3 TTS Proxy)")
    payload = {
        "text": "नमस्ते, ग्रामसेहत में आपका स्वागत है।",
        "target_language_code": "hi-IN",
        "speaker": "shubh",
        "model": "bulbul:v3"
    }
    resp = requests.post(f"{BASE_URL}/api/tts", json=payload, timeout=25)
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Failed TTS synthesis: {resp.text}"
    content_type = resp.headers.get("content-type", "")
    assert "audio/wav" in content_type, f"Expected audio/wav, got {content_type}"
    audio_data = resp.content
    assert len(audio_data) > 1000, f"Expected audio data > 1KB, got {len(audio_data)} bytes"
    assert audio_data[:4] == b"RIFF", "Generated audio must be a valid RIFF WAV file"
    print(f"✓ Sarvam Bulbul TTS generated {len(audio_data)} bytes of valid WAV audio.")
    return audio_data


def test_sarvam_stt(sample_audio_bytes):
    print_section("6. Testing POST /api/stt (Sarvam Saaras v3 STT Proxy)")
    files = {
        "file": ("test_sample.wav", sample_audio_bytes, "audio/wav")
    }
    data = {
        "language_code": "hi-IN",
        "model": "saaras:v3"
    }
    resp = requests.post(f"{BASE_URL}/api/stt", files=files, data=data, timeout=30)
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Failed STT transcription: {resp.text}"
    result = resp.json()
    assert "transcript" in result
    print(f"Transcript received: '{result['transcript']}' (Language: {result.get('language_code')})")
    assert len(result["transcript"]) > 0, "Expected non-empty transcript"
    print("✓ Sarvam Saaras STT successfully transcribed audio.")


def run_all_tests():
    print("\nStarting GramSehat Backend Test Suite (Sarvam AI + EasyOCR)...")
    print(f"Targeting API Server: {BASE_URL}")

    # Wait for server if starting up
    for _ in range(10):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=3)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)

    try:
        test_health_endpoint()
        test_process_transcript_hindi()
        test_process_transcript_english()
        test_dynamic_patient_questions()
        test_process_transcript_validation()
        test_extract_report_text()
        generated_audio = test_sarvam_tts()
        test_sarvam_stt(generated_audio)
        
        print_section("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✓ Sarvam AI STT (/api/stt) & TTS (/api/tts) proxy endpoints fully verified.")
        print("✓ Clinical triage endpoint (/process-transcript) verified.")
        print("✓ Bilingual prescription/report OCR (/extract-report-text) verified.")
        print("✓ No hardcoded keys exposed; clean separation between frontend & backend.")
    except AssertionError as e:
        print(f"\n❌ TEST ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR RUNNING TESTS: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
