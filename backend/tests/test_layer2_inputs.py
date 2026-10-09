"""
Test Suite for GramSehat Layer 2: Input Processing
==================================================
Tests:
- Audio transcription via Sarvam AI Saaras (Hindi & Hinglish codemix)
- Medical prescription & lab report OCR via EasyOCR (English & Hindi)
- Oversized audio rejection (>10 MB)
- Over-length audio rejection (>30s)
- Corrupt / empty audio rejection
- Blank / unreadable image rejection
- 1-retry mechanism on 5xx and network timeout
- Direct Python function imports for Layer 6
- FastAPI HTTP endpoints (POST /transcribe-audio, POST /extract-report-text)
"""

import io
import unittest
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services import extract_report_text, transcribe_audio
from app.services.sarvam_stt_client import SarvamSTTClient

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_assets"


def generate_silent_wav(duration_seconds: float, sample_rate: int = 16000) -> bytes:
    """Helper to synthesize a standard PCM WAV buffer with arbitrary duration."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        num_frames = int(duration_seconds * sample_rate)
        w.writeframes(b"\x00\x00" * num_frames)
    return buf.getvalue()


class TestLayer2InputProcessing(unittest.TestCase):
    """Unit and integration test cases for Layer 2 speech and document OCR."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.wav_path = SAMPLE_DIR / "hindi_symptom_audio.wav"
        cls.prescription_path = SAMPLE_DIR / "sample_prescription.png"
        cls.blank_image_path = SAMPLE_DIR / "sample_blank_image.png"

    # --------------------------------------------------------------------------
    # 1. AUDIO REJECTION CONSTRAINTS
    # --------------------------------------------------------------------------

    def test_01_empty_audio_bytes_rejected(self):
        """Audio under 100 bytes must be rejected with HTTP 400 Bad Request."""
        tiny_audio = b"RIFF" + b"\x00" * 20
        with self.assertRaises(HTTPException) as ctx:
            transcribe_audio(tiny_audio, filename="tiny.wav")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("empty or corrupted", ctx.exception.detail.lower())

    def test_02_oversized_audio_rejected_over_10mb(self):
        """Audio payload exceeding 10 MB must be rejected with HTTP 413."""
        big_audio = b"\x00" * (11 * 1024 * 1024)  # 11 MB
        with self.assertRaises(HTTPException) as ctx:
            transcribe_audio(big_audio, filename="big.wav")
        self.assertEqual(ctx.exception.status_code, 413)
        self.assertIn("exceeds maximum allowed limit", ctx.exception.detail)

    def test_03_audio_duration_over_30_seconds_rejected(self):
        """Audio longer than 30 seconds must be rejected with HTTP 400."""
        long_wav_bytes = generate_silent_wav(duration_seconds=35.0)
        with self.assertRaises(HTTPException) as ctx:
            transcribe_audio(long_wav_bytes, filename="35sec.wav")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("exceeds the maximum allowed limit of 30 seconds", ctx.exception.detail)

    # --------------------------------------------------------------------------
    # 2. AUDIO TRANSCRIPTION VIA SARVAM AI (HINDI & CODEMIX)
    # --------------------------------------------------------------------------

    def test_04_transcribe_audio_hindi_live(self):
        """Short Hindi voice recording transcribes accurately via Sarvam Saaras v3."""
        if not self.wav_path.exists():
            self.skipTest("Sample wav asset not found")

        with open(self.wav_path, "rb") as f:
            audio_bytes = f.read()

        result = transcribe_audio(
            file_bytes=audio_bytes,
            filename="hindi_symptom.wav",
            language_code="hi-IN",
            mode="transcribe"
        )

        self.assertIn("transcribed_text", result)
        self.assertIn("language", result)
        self.assertEqual(result["mode"], "transcribe")
        self.assertTrue(len(result["transcribed_text"]) > 10)
        # Verify Hindi symptoms like bukhar (fever) or dard (pain)
        text = result["transcribed_text"]
        self.assertTrue("बुखार" in text or "दर्द" in text or "डॉक्टर" in text)

    def test_05_transcribe_audio_hinglish_codemix_live(self):
        """Audio processed in codemix mode returns valid code-mixed Hinglish output."""
        if not self.wav_path.exists():
            self.skipTest("Sample wav asset not found")

        with open(self.wav_path, "rb") as f:
            audio_bytes = f.read()

        result = transcribe_audio(
            file_bytes=audio_bytes,
            filename="hindi_symptom.wav",
            language_code="hi-IN",
            mode="codemix"
        )

        self.assertIn("transcribed_text", result)
        self.assertEqual(result["mode"], "codemix")
        self.assertTrue(len(result["transcribed_text"]) > 10)

    # --------------------------------------------------------------------------
    # 3. DOCUMENT OCR EXTRACTION VIA EASYOCR
    # --------------------------------------------------------------------------

    def test_06_extract_report_text_prescription_live(self):
        """Prescription image returns both raw OCR text and clean text."""
        if not self.prescription_path.exists():
            self.skipTest("Sample prescription asset not found")

        with open(self.prescription_path, "rb") as f:
            image_bytes = f.read()

        result = extract_report_text(image_bytes)
        self.assertIn("raw_text", result)
        self.assertIn("cleaned_text", result)

        raw = result["raw_text"]
        clean = result["cleaned_text"]
        self.assertTrue(len(raw) > 20)
        self.assertTrue(len(clean) > 20)

        # Check expected medical content
        combined = f"{raw} {clean}".lower()
        self.assertTrue("paracetamol" in combined or "health" in combined or "clinic" in combined or "bp" in combined)

    def test_07_extract_report_text_blank_image_rejected(self):
        """Blank image with no readable text raises HTTP 422 unprocessable entity."""
        if not self.blank_image_path.exists():
            self.skipTest("Sample blank image not found")

        with open(self.blank_image_path, "rb") as f:
            blank_bytes = f.read()

        with self.assertRaises(HTTPException) as ctx:
            extract_report_text(blank_bytes)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertIn("no readable text", ctx.exception.detail.lower())

    # --------------------------------------------------------------------------
    # 4. NETWORK RETRY & TIMEOUT MECHANISM
    # --------------------------------------------------------------------------

    @patch("requests.post")
    def test_08_retry_on_transient_500_server_error(self, mock_post):
        """Client automatically retries once on 5xx and succeeds on 2nd attempt."""
        # 1st attempt: 500 error, 2nd attempt: 200 OK
        resp_500 = MagicMock(status_code=500, ok=False, text="Internal Server Error")
        resp_200 = MagicMock(
            status_code=200,
            ok=True,
            json=lambda: {"transcript": "नमस्ते डॉक्टर", "language_code": "hi-IN"}
        )
        mock_post.side_effect = [resp_500, resp_200]

        client = SarvamSTTClient(api_key="mock_key", max_retries=1, timeout=5.0)
        audio_payload = generate_silent_wav(duration_seconds=3.0)

        res = client.transcribe(audio_payload, filename="test.wav")
        self.assertEqual(res["transcribed_text"], "नमस्ते डॉक्टर")
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_09_timeout_exhausts_retries_and_returns_504(self, mock_post):
        """Client times out after retry budget and raises HTTP 504 Gateway Timeout."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

        client = SarvamSTTClient(api_key="mock_key", max_retries=1, timeout=0.5)
        audio_payload = generate_silent_wav(duration_seconds=2.0)

        with self.assertRaises(HTTPException) as ctx:
            client.transcribe(audio_payload, filename="test.wav")
        self.assertEqual(ctx.exception.status_code, 504)
        self.assertIn("timed out", ctx.exception.detail.lower())
        self.assertEqual(mock_post.call_count, 2)

    # --------------------------------------------------------------------------
    # 5. FASTAPI HTTP ROUTE INTEGRATION
    # --------------------------------------------------------------------------

    def test_10_post_transcribe_audio_http_endpoint(self):
        """POST /transcribe-audio endpoint returns 200 with schema compliant output."""
        if not self.wav_path.exists():
            self.skipTest("Sample wav asset not found")

        with open(self.wav_path, "rb") as f:
            wav_bytes = f.read()

        response = self.client.post(
            "/transcribe-audio",
            files={"file": ("symptom.wav", wav_bytes, "audio/wav")},
            data={"language_code": "hi-IN", "mode": "transcribe"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("transcribed_text", data)
        self.assertIn("language", data)
        self.assertEqual(data["mode"], "transcribe")
        self.assertTrue(len(data["transcribed_text"]) > 5)

    def test_11_post_extract_report_text_http_endpoint(self):
        """POST /extract-report-text endpoint returns 200 with raw and cleaned text."""
        if not self.prescription_path.exists():
            self.skipTest("Sample prescription asset not found")

        with open(self.prescription_path, "rb") as f:
            img_bytes = f.read()

        response = self.client.post(
            "/extract-report-text",
            files={"file": ("prescription.png", img_bytes, "image/png")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("raw_text", data)
        self.assertIn("cleaned_text", data)
        self.assertTrue(len(data["raw_text"]) > 10)

    # --------------------------------------------------------------------------
    # 6. LAYER 6 DIRECT IMPORT COMPATIBILITY
    # --------------------------------------------------------------------------

    def test_12_layer6_direct_import_contract(self):
        """Verifies that Layer 6 can import both functions directly."""
        from app.services.input_processing import extract_report_text as l6_ocr
        from app.services.input_processing import transcribe_audio as l6_stt

        self.assertTrue(callable(l6_stt))
        self.assertTrue(callable(l6_ocr))


if __name__ == "__main__":
    unittest.main()
