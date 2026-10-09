# GramSehat — Backend Module

Backend service supporting the GramSehat rural healthcare application.
- **Voice Pipeline**: Powered by **Sarvam AI** for high-accuracy Indian vernacular voice:
  - **Speech-to-Text (STT)**: Sarvam `saaras:v3` via `POST /api/stt`
  - **Text-to-Speech (TTS)**: Sarvam `bulbul:v3` (voices: "shubh", "priya", "kavya") via `POST /api/tts`
- **Transcript Ingestion**: Exposes `POST /process-transcript` to receive final symptom text directly from the client for clinical triage and LLM reasoning.
- **Bilingual Medical OCR**: Uses `EasyOCR` (`['en', 'hi']`) to decode printed and handwritten prescriptions and laboratory reports.

---

## 📌 Architecture Overview

```
+-------------------------------------------------------------+
| CLIENT LAYER (MediaRecorder & HTML5 Audio)                  |
|                                                             |
|  1. Speech-to-Text (STT):                                   |
|     - MediaRecorder captures audio (up to 25s auto-stop)    |
|     - Forwards audio blob to POST /api/stt                  |
|     - Sarvam Saaras v3 transcribes Hindi (hi-IN) / English  |
|                                                             |
|  2. Text-to-Speech (TTS):                                   |
|     - Calls POST /api/tts proxy                             |
|     - Sarvam Bulbul v3 synthesizes high-quality audio       |
|     - HTML5 Audio sequential playback with sentence split   |
+──────────────────────────────┬──────────────────────────────+
                               │ Final Transcript Text
                               ▼
+─────────────────────────────────────────────────────────────+
| BACKEND API (FastAPI)                                       |
|                                                             |
|  POST /process-transcript       POST /extract-report-text   |
|  ┌───────────────────────┐      ┌─────────────────────────┐ |
|  │ Clinical Triage Logic │      │ EasyOCR (['en', 'hi'])  │ |
|  │ Evaluates Acuity      │      │ Bilingual OCR Reader    │ |
|  │ Prepares Guidance     │      │ (Single startup load)   │ |
|  └──────────┬────────────┘      └────────────┬────────────┘ |
|             │                                │              |
|             ▼                                ▼              |
|  Clinical Assessment & Speech     Clean Extracted Text      |
+─────────────────────────────────────────────────────────────+
```

---

## 📡 API Endpoints

### 1. Transcribe Voice Audio (Layer 2: Sarvam AI Saaras)
- **Endpoint**: `POST /transcribe-audio`
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (audio binary), `language_code` (default: `"hi-IN"`), `mode` (default: `"transcribe"`, or `"codemix"`)
- **Response (200 OK)**:
  ```json
  {
    "transcribed_text": "नमस्ते डॉक्टर साहब, मुझे पिछले दो दिनों से तेज बुखार है।",
    "language": "hi-IN",
    "mode": "transcribe"
  }
  ```

### 2. Extract Document Text (Layer 2: EasyOCR)
- **Endpoint**: `POST /extract-report-text`
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (image photo: jpg, png, webp)
- **Response (200 OK)**:
  ```json
  {
    "raw_text": "Tab Paracetamol 650mg\nBP 130/85 mmHg",
    "cleaned_text": "Tab Paracetamol 650mg\nBP 130/85 mmHg"
  }
  ```

### 3. Process Symptom Transcript
- **Endpoint**: `POST /process-transcript`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "transcript": "कल से बहुत चक्कर और कमजोरी महसूस हो रहे हैं",
    "language": "hi-IN"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "transcript": "कल से बहुत चक्कर और कमजोरी महसूस हो रहे हैं",
    "language": "hi-IN",
    "scenario_match": "dizziness",
    "urgency_level": "border-moderate",
    "urgency_title": "क्लिनिक जांच की सलाह",
    "care_level": "24 घंटे के अंदर क्लिनिक परामर्श",
    "why_matters": "लगातार कमजोरी और चक्कर शरीर में हीमोग्लोबिन की कमी (एनीमिया), निर्जलीकरण अथवा निम्न रक्तचाप के कारण हो सकते हैं।",
    "what_to_do": "आराम से बैठें या लेटें। अचानक खड़े होने से बचें। ओआरएस या नींबू पानी पिएं।",
    "nearest_care": "सामुदायिक स्वास्थ्य केंद्र (CHC) मोहनलालगंज — 3.1 किमी",
    "ai_response_speech": "नमस्ते। आपकी कमजोरी और चक्कर के लिए पर्याप्त आराम और ओआरएस घोल लेना जरूरी है। कल सुबह नजदीकी स्वास्थ्य केंद्र में खून की जांच अवश्य करवाएं।"
  }
  ```

---

### 2. Extract Report / Prescription Text
- **Endpoint**: `POST /extract-report-text`
- **Content-Type**: `multipart/form-data`
- **Parameters**: `file` (image binary: PNG, JPEG, WebP)
- **Response (200 OK)**:
  ```json
  {
    "raw_text": "GRAMSEHAT RURAL HEALTH CLINIC\nPatient Name: Ram Lal\nBP 130/85 mmHg\nTab Paracetamol 650mg 1 गोली दिन में दो बार...",
    "cleaned_text": "GRAMSEHAT RURAL HEALTH CLINIC\nPatient Name: Ram Lal\nBP 130/85 mmHg\nTab Paracetamol 650mg 1 गोली दिन में दो बार..."
  }
  ```

---

### 3. Layer 4: AI Reasoning Endpoints (Sarvam AI LLM)

Powered by **Sarvam AI** (Sarvam-30B and Sarvam-105B) via the OpenAI-compatible API (`https://api.sarvam.ai/v1`).
Optimized for rural Hindi-English code-switched patient communication and clinical structuring.

#### A. Symptom Structuring (Speed-critical, Sarvam-30B)
- **Endpoint**: `POST /structure-symptoms`
- **Method**: `POST`
- **Model**: `sarvam-30b` (with auto-fallback to `sarvam-105b-conversations`)
- **Request Body**:
  ```json
  {
    "text": "नमस्ते डॉक्टर, मुझे पिछले दो दिनों से बहुत तेज़ बुखार और सिरदर्द है।",
    "language": "hi-IN"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "symptoms": ["Tez bukhar (High fever)", "Sirdard (Headache)"],
    "duration": "2 din (2 days)",
    "severity_notes": "Patient reports severe fever and headache persisting for two days.",
    "follow_up_question": "क्या बुखार के साथ आपको ठंड या कंपकंपी भी महसूस हो रही है?"
  }
  ```

#### B. Medical Report / Prescription Explanation (Accuracy-critical, Sarvam-105B)
- **Endpoint**: `POST /explain-report`
- **Method**: `POST`
- **Model**: `sarvam-105b-conversations`
- **Request Body**:
  ```json
  {
    "report_text": "COMPLETE BLOOD COUNT: Hemoglobin 8.2 g/dL (Normal 13-17), Serum Ferritin 11 ng/mL (Normal 20-250)",
    "patient_query": "Why am I feeling so weak and dizzy?",
    "language": "en"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "explanation": "Your blood report shows that your hemoglobin is lower than normal, which means your body has less oxygen-carrying strength. Additionally, your body's stored iron reserves are running low, explaining your recent weakness and dizziness. Your other blood counts are healthy and functioning normally. With proper iron-rich nourishment and guidance from your local doctor, your energy levels can gradually recover.",
    "flagged_values": [
      {
        "test_name": "Hemoglobin (Hb)",
        "value": "8.2 g/dL",
        "reference_range": "13.0 - 17.0",
        "status": "low",
        "simple_meaning": "The red oxygen and energy carriers in your blood are below normal, leading to tiredness and lightheadedness."
      },
      {
        "test_name": "Serum Ferritin",
        "value": "11 ng/mL",
        "reference_range": "20 - 250",
        "status": "low",
        "simple_meaning": "The body's natural storage supply of iron is depleted."
      }
    ]
  }
  ```

#### C. Hospital Handover Summary Generation (Accuracy-critical, Sarvam-105B)
- **Endpoint**: `POST /generate-hospital-summary`
- **Method**: `POST`
- **Model**: `sarvam-105b-conversations`
- **Request Body**:
  ```json
  {
    "patient_name": "Ramlal Sharma",
    "age": 54,
    "gender": "Male",
    "village": "Shivpur Village",
    "symptoms": ["Severe dizziness", "Postural lightheadedness", "Extreme weakness"],
    "duration": "2 days, worsening since morning",
    "vitals": {"BP": "94/60 mmHg", "Pulse": "104 bpm", "SpO2": "97%"},
    "report_findings": "Hb 8.2 g/dL, Ferritin 11 ng/mL",
    "screening_flags": {"conjunctival_pallor": "positive (0.78)"}
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "summary": "SITUATION: Ramlal Sharma, 54M from Shivpur Village, presents with severe dizziness and extreme weakness worsening over 2 days. BACKGROUND: Acute-on-chronic decompensation with symptomatic iron deficiency anemia (Hb 8.2 g/dL, Ferritin 11 ng/mL). ASSESSMENT: Borderline hypotension and compensatory tachycardia (BP 94/60, Pulse 104 bpm, SpO2 97%). Screening positive for conjunctival pallor (0.78) and cold extremities. RECOMMENDATION: Secure IV access, repeat postural vitals, maintain strict fall precautions, and evaluate for volume resuscitation and parenteral iron therapy."
  }
  ```

---

### 4. Health Check
- **Endpoint**: `GET /health`
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "service": "GramSehat Backend",
    "voice_pipeline": {
      "provider": "Sarvam AI",
      "stt": "Sarvam Speech-to-Text (saaras:v3)",
      "tts": "Sarvam Text-to-Speech (bulbul:v3)",
      "default_speaker": "shubh",
      "proxy_endpoints": ["/api/stt", "/api/tts"]
    },
    "layer4_ai_reasoning": {
      "status": "active",
      "provider": "Sarvam AI (OpenAI-compatible API)",
      "models": {
        "symptom_structuring": "sarvam-30b",
        "report_explanation": "sarvam-105b-conversations",
        "hospital_summary": "sarvam-105b-conversations",
        "fallback": "sarvam-105b-conversations"
      },
      "retry_policy": "1 retry"
    },
    "models": {
      "easyocr": {
        "loaded": true,
        "languages": ["en", "hi"]
      }
    }
---

### 6. Assess Clinical Urgency (Layer 5: Safety Rule Engine)
- **Endpoint**: `POST /assess-urgency`
- **Purpose**: Pure deterministic, config-driven clinical urgency evaluation based on WHO / IMCI danger-sign guidance. Zero LLM/ML dependencies.
- **Request Body**:
  ```json
  {
    "structured_symptoms": ["chest_pain"],
    "raw_text": "सीने में बहुत तेज दर्द है और सांस लेने में भारी दिक्कत हो रही है",
    "screening_flags": ["pallor_screening_flag"],
    "patient": {
      "age": 52,
      "is_pregnant": false
    }
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "urgency": "red",
    "triggered_rules": ["RED_CHEST_CARDIAC"],
    "reason": "Chest pain combined with breathlessness, sweating, or pain radiating to the left arm indicates a high likelihood of acute myocardial infarction (heart attack).",
    "recommended_action": "Immediate emergency transfer to nearest hospital with cardiology and ICU facility. Keep patient at rest and do not permit physical exertion.",
    "required_specialty": "Cardiology",
    "follow_up_question": null
  }
  ```

---

## ⚙️ Configuration & Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `SARVAM_API_KEY` | *(Configured)* | Sarvam AI API Key for Voice STT/TTS and Layer 4 LLM Reasoning |
| `SARVAM_REASONING_BASE_URL` | `https://api.sarvam.ai/v1` | OpenAI-compatible base URL for Sarvam LLMs |
| `SARVAM_MODEL_SYMPTOM_STRUCTURING`| `sarvam-30b` | Model for symptom extraction (speed-critical) |
| `SARVAM_MODEL_REPORT_EXPLANATION` | `sarvam-105b-conversations` | Model for lab report plain-language breakdown |
| `SARVAM_MODEL_HOSPITAL_SUMMARY`   | `sarvam-105b-conversations` | Model for hospital SBAR handover summary |
| `SARVAM_MODEL_FALLBACK`           | `sarvam-105b-conversations` | Active cluster fallback model |
| `SARVAM_MAX_RETRIES`              | `1` | Automatic retry budget on timeout or malformed JSON |
| `MAX_IMAGE_SIZE_MB`               | `15` | Maximum upload size for prescriptions/reports |
| `OCR_GPU`                         | `false` | Enable GPU acceleration for EasyOCR |

---

## 🚀 Running the Server

```bash
cd backend
source venv/bin/activate
./run.sh
```

Or directly via Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --lifespan on
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.
