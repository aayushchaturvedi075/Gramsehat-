import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.triage import TranscriptRequest, ClinicalTriageResponse
from app.schemas.error import ErrorResponse

from app.services.sarvam_reasoning_service import sarvam_reasoning_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Clinical Reasoning & Transcript Triage"])


@router.post(
    "/process-transcript",
    response_model=ClinicalTriageResponse,
    status_code=status.HTTP_200_OK,
    summary="Process patient question or symptom transcript text",
    description=(
        "Receives symptom transcript or health question text from Sarvam AI STT or manual input. "
        "Evaluates clinical acuity using Sarvam AI LLM reasoning and returns structured guidance "
        "and dynamic, empathetic spoken AI feedback tailored directly to the patient's question."
    ),
    responses={
        200: {
            "model": ClinicalTriageResponse,
            "description": "Clinical assessment completed successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Empty or invalid transcript text provided."
        }
    }
)
async def process_transcript(payload: TranscriptRequest) -> ClinicalTriageResponse:
    """
    Dynamic clinical reasoning and triage endpoint for patient queries and symptoms.
    Uses Sarvam AI LLM reasoning to generate context-aware answers tailored directly to what was asked.
    """
    clean_text = payload.transcript.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript text is empty. Please speak or enter valid symptoms."
        )

    lang = payload.language or "en-IN"
    logger.info("Processing patient query via Sarvam LLM reasoning [%s]: '%s'", lang, clean_text)

    try:
        triage_data = sarvam_reasoning_service.triage_patient_query(
            transcript=clean_text,
            language=lang,
            history=payload.history
        )
        return ClinicalTriageResponse(**triage_data)
    except Exception as exc:
        logger.error("Error during Sarvam LLM triage reasoning: %s. Using safety fallback.", exc)
        # In case of unhandled exception, return safe structured response
        is_hindi = lang.startswith("hi") or any("\u0900" <= ch <= "\u097F" for ch in clean_text)
        return ClinicalTriageResponse(
            transcript=clean_text,
            language="hi-IN" if is_hindi else "en-IN",
            scenario_match="general_health",
            urgency_level="border-moderate",
            urgency_title="चिकित्सा परामर्श की सलाह" if is_hindi else "Medical Guidance Advised",
            care_level="24 घंटे में क्लिनिक में दिखाएं" if is_hindi else "Clinic Check-up within 24 Hours",
            why_matters=(
                "आपके बताए गए लक्षणों के लिए डॉक्टर से व्यक्तिगत परामर्श लेना आवश्यक है ताकि सही कारण का पता चल सके।"
                if is_hindi else
                "Your reported symptoms warrant clinical evaluation to identify the underlying cause."
            ),
            what_to_do=(
                "पर्याप्त आराम करें, साफ पानी पिएं और नजदीकी स्वास्थ्य केंद्र में डॉक्टर से जांच करवाएं।"
                if is_hindi else
                "Rest well, stay hydrated, and consult a doctor at your nearest health centre."
            ),
            nearest_care=(
                "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी"
                if is_hindi else
                "Primary Health Centre (PHC) Shivpur — 1.8 km"
            ),
            ai_response_speech=(
                "नमस्ते। आपके लक्षणों के लिए कृपया थोड़ा आराम करें और नजदीकी स्वास्थ्य केंद्र पर जाकर डॉक्टर से सलाह लें।"
                if is_hindi else
                "Hello. Please rest and visit your local health centre for personalized clinical guidance."
            )
        )
