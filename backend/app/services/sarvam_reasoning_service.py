"""
Layer 4 Service: Sarvam AI Reasoning Engine.
Integrates Sarvam AI LLMs (Sarvam-30B and Sarvam-105B) via their OpenAI-compatible API
for symptom structuring, medical report explanations, and SBAR hospital clinical handover summaries.
"""

import json
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional

import openai
from openai import OpenAI

from app.config import settings
from app.prompts import (
    build_symptom_structuring_messages,
    build_report_explanation_messages,
    build_hospital_summary_messages,
    build_triage_messages,
)
from app.schemas.reasoning import (
    SymptomStructureResponse,
    ReportExplanationResponse,
    HospitalSummaryResponse,
    FlaggedValue,
)

logger = logging.getLogger(__name__)


class SarvamReasoningService:
    """
    Manages Sarvam AI LLM interactions for Layer 4 AI Reasoning.
    Implements structured JSON extraction, configurable model switching (Sarvam-30B/105B),
    robust 1-retry handling, and graceful safe fallbacks to protect downstream Layer 5.
    """

    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        """Lazy-initializes and returns the OpenAI client configured for Sarvam AI."""
        if self._client is None:
            api_key = settings.SARVAM_API_KEY.strip()
            if not api_key:
                logger.warning("SARVAM_API_KEY is not configured in settings or environment!")

            logger.info("Initializing OpenAI client for Sarvam AI LLM reasoning at %s...", settings.SARVAM_REASONING_BASE_URL)
            self._client = OpenAI(
                base_url=settings.SARVAM_REASONING_BASE_URL,
                api_key=api_key or "sk_placeholder",
                default_headers={"api-subscription-key": api_key or "sk_placeholder"},
                timeout=settings.SARVAM_REQUEST_TIMEOUT
            )
        return self._client

    def _resolve_model(self, requested_model: Optional[str], default_model: str) -> str:
        """Resolves active model name with configurable defaults."""
        return requested_model or default_model or settings.SARVAM_MODEL_FALLBACK

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Defensively extracts and parses JSON from Sarvam model response.
        Handles markdown code blocks (```json ... ```) and leading/trailing chatter.
        """
        text = raw_text.strip()

        # Remove surrounding markdown fences ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback regex search for the outermost balanced { ... } object
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def _call_sarvam_with_retry(
        self,
        messages: List[Dict[str, str]],
        target_model: str,
        operation_name: str,
        fallback_factory: Callable[[], Any],
        max_tokens: int = 450,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Executes chat completion with OpenAI SDK against Sarvam AI.
        Implements 1 retry on timeout, transient network/API issues, or malformed JSON.
        Returns fallback structure if all retries are exhausted.
        """
        attempt = 0
        current_model = target_model
        last_error = None
        current_messages = list(messages)
        last_raw_response = None

        max_attempts = settings.SARVAM_MAX_RETRIES + 1

        while attempt < max_attempts:
            attempt += 1
            try:
                logger.info(
                    "Executing Layer 4 Sarvam AI Reasoning [%s] (attempt %d/%d) using model '%s'",
                    operation_name, attempt, max_attempts, current_model
                )

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=current_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                if not response.choices or not response.choices[0].message:
                    raise ValueError(f"Empty choices returned from model '{current_model}'")

                content = response.choices[0].message.content
                last_raw_response = content

                if not content or not content.strip():
                    raise ValueError(f"Empty content returned from model '{current_model}'")

                parsed_json = self._clean_and_parse_json(content)
                logger.info(
                    "Layer 4 Sarvam AI Reasoning [%s] succeeded on attempt %d using '%s'",
                    operation_name, attempt, current_model
                )
                return parsed_json

            except openai.BadRequestError as bre:
                last_error = bre
                err_msg = str(bre).lower()
                # Handle model deprecation (e.g. sarvam-30b -> sarvam-105b-conversations)
                if ("deprecated" in err_msg or "not found" in err_msg or "invalid" in err_msg) and current_model != settings.SARVAM_MODEL_FALLBACK:
                    logger.warning(
                        "Model '%s' rejected by Sarvam API (%s). Switching to fallback model '%s'.",
                        current_model, bre, settings.SARVAM_MODEL_FALLBACK
                    )
                    current_model = settings.SARVAM_MODEL_FALLBACK
                    # Retry immediately with active model
                    continue
                else:
                    logger.warning("BadRequestError in [%s] attempt %d: %s", operation_name, attempt, bre)

            except json.JSONDecodeError as jerr:
                last_error = jerr
                logger.warning(
                    "Malformed JSON from Sarvam model '%s' in [%s] on attempt %d: %s. Raw: %s",
                    current_model, operation_name, attempt, jerr, (last_raw_response or "")[:200]
                )
                if attempt < max_attempts:
                    current_messages = list(messages) + [
                        {
                            "role": "assistant",
                            "content": last_raw_response or "{}"
                        },
                        {
                            "role": "user",
                            "content": (
                                "CRITICAL FIX: Your previous response was not valid JSON. "
                                "You must return strictly a single, 100% valid JSON object matching the required schema. "
                                "Do NOT include explanations or markdown outside the JSON."
                            )
                        }
                    ]
                    time.sleep(0.5)

            except (openai.APITimeoutError, openai.APIConnectionError) as terr:
                last_error = terr
                logger.warning("Sarvam API network/timeout error in [%s] on attempt %d: %s", operation_name, attempt, terr)
                time.sleep(1.0)

            except openai.RateLimitError as rerr:
                last_error = rerr
                logger.warning("Sarvam API rate limit (429) in [%s] on attempt %d: %s", operation_name, attempt, rerr)
                time.sleep(1.5)

            except Exception as exc:
                last_error = exc
                logger.warning("Unexpected error in [%s] on attempt %d with model '%s': %s", operation_name, attempt, current_model, exc)
                time.sleep(1.0)

        # Fallback path: All retries failed. Log raw response and return safe fallback.
        logger.error(
            "Layer 4 Sarvam Reasoning [%s] exhausted %d attempts. Last error: %s. Raw response: %s. Activating safe fallback.",
            operation_name, attempt, last_error, (last_raw_response or "None")
        )
        return fallback_factory()

    def structure_symptoms(
        self,
        text: str,
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> SymptomStructureResponse:
        """
        Speed-critical: Parses informal rural Hindi/English patient speech into structured clinical data.
        Uses Sarvam-30B (or configured default) with automatic fallback.
        """
        chosen_model = self._resolve_model(model, settings.SARVAM_MODEL_SYMPTOM_STRUCTURING)
        messages = build_symptom_structuring_messages(text, language)

        def fallback_symptoms():
            return {
                "symptoms": ["Patient-reported health concern requires clinical intake"],
                "duration": "Not specified",
                "severity_notes": f"Raw intake transcript: {text[:200]}",
                "follow_up_question": "क्या आप अपने लक्षणों के बारे में थोड़ा और विस्तार से बता सकते हैं?"
            }

        raw_data = self._call_sarvam_with_retry(
            messages=messages,
            target_model=chosen_model,
            operation_name="structure-symptoms",
            fallback_factory=fallback_symptoms,
            max_tokens=350,
            temperature=0.2
        )

        symptoms = raw_data.get("symptoms", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        elif not isinstance(symptoms, list) or not symptoms:
            symptoms = ["Patient-reported health concern requires clinical intake"]

        duration = str(raw_data.get("duration") or "Not specified")
        severity_notes = str(raw_data.get("severity_notes") or "Patient provided symptom description")
        follow_up = raw_data.get("follow_up_question")
        if follow_up and isinstance(follow_up, str):
            follow_up = follow_up.strip() or None
        else:
            follow_up = None

        return SymptomStructureResponse(
            symptoms=[str(s) for s in symptoms],
            duration=duration,
            severity_notes=severity_notes,
            follow_up_question=follow_up
        )

    def explain_report(
        self,
        report_text: str,
        patient_query: Optional[str] = None,
        screening_context: Optional[dict] = None,
        language: str = "en",
        model: Optional[str] = None
    ) -> ReportExplanationResponse:
        """
        Accuracy-critical: Explains medical report or prescription OCR text to rural patients.
        Uses Sarvam-105B. Strictly constrained to 3-5 sentences in simple Hindi/English mix.
        """
        chosen_model = self._resolve_model(model, settings.SARVAM_MODEL_REPORT_EXPLANATION)
        messages = build_report_explanation_messages(
            report_text=report_text,
            patient_query=patient_query,
            screening_context=screening_context,
            language=language
        )

        def fallback_report():
            is_hi = language and language.startswith("hi")
            return {
                "explanation": (
                    "आपकी मेडिकल रिपोर्ट प्राप्त हो गई है। इसमें दी गई जांचों की पुष्टि के लिए कृपया नजदीकी स्वास्थ्य केंद्र पर डॉक्टर से संपर्क करें। डॉक्टर आपके स्वास्थ्य के अनुसार सही दवा और सलाह देंगे।"
                    if is_hi
                    else "Your medical report has been received and reviewed. Please share this report with your healthcare practitioner or primary clinic doctor for clinical correlation. They will provide the appropriate guidance and treatment."
                ),
                "flagged_values": []
            }

        raw_data = self._call_sarvam_with_retry(
            messages=messages,
            target_model=chosen_model,
            operation_name="explain-report",
            fallback_factory=fallback_report,
            max_tokens=500,
            temperature=0.2
        )

        explanation = str(raw_data.get("explanation", "")).strip()
        if not explanation:
            explanation = (
                "रिपोर्ट का सारांश: कृपया अपने प्राथमिक स्वास्थ्य केंद्र पर जाकर डॉक्टर से सलाह लें।"
                if language and language.startswith("hi")
                else "Report summary: Please consult your local primary health centre doctor for advice."
            )

        flagged_raw = raw_data.get("flagged_values", [])
        if not isinstance(flagged_raw, list):
            flagged_raw = []

        flagged_values: List[FlaggedValue] = []
        for item in flagged_raw:
            if isinstance(item, dict):
                flagged_values.append(
                    FlaggedValue(
                        test_name=str(item.get("test_name") or item.get("metric") or "Investigation"),
                        value=str(item.get("value") or "N/A"),
                        reference_range=item.get("reference_range") or item.get("reference"),
                        status=str(item.get("status") or "abnormal"),
                        simple_meaning=str(item.get("simple_meaning") or item.get("meaning") or "Clinical assessment recommended")
                    )
                )

        return ReportExplanationResponse(
            explanation=explanation,
            flagged_values=flagged_values
        )

    def generate_hospital_summary(
        self,
        dossier: Dict[str, Any],
        model: Optional[str] = None
    ) -> HospitalSummaryResponse:
        """
        Accuracy-critical: Synthesizes patient dossier into professional SBAR pre-arrival handover summary.
        Uses Sarvam-105B for comprehensive clinical reasoning.
        """
        chosen_model = self._resolve_model(model, settings.SARVAM_MODEL_HOSPITAL_SUMMARY)
        messages = build_hospital_summary_messages(dossier)

        def fallback_hospital():
            p_name = dossier.get("patient_name", "Patient")
            p_symp = dossier.get("symptoms", "Recorded symptoms")
            p_vit = dossier.get("vitals", "Pending triage vitals")
            return {
                "summary": (
                    f"SBAR CLINICAL HANDOVER (CONTINGENCY):\n"
                    f"S - Situation: Patient {p_name} presenting for rural emergency/clinical transfer.\n"
                    f"B - Background: Reported complaints: {p_symp}.\n"
                    f"A - Assessment: Intake vitals: {p_vit}. Full baseline parameters pending physical evaluation.\n"
                    f"R - Recommendation: Perform immediate primary survey, establish IV access as needed, and monitor vitals on arrival."
                )
            }

        raw_data = self._call_sarvam_with_retry(
            messages=messages,
            target_model=chosen_model,
            operation_name="generate-hospital-summary",
            fallback_factory=fallback_hospital,
            max_tokens=600,
            temperature=0.2
        )

        summary_text = str(raw_data.get("summary", "")).strip()
        if not summary_text:
            summary_text = fallback_hospital()["summary"]

        return HospitalSummaryResponse(summary=summary_text)

    def triage_patient_query(
        self,
        transcript: str,
        language: Optional[str] = "en-IN",
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes patient health query or symptom transcript using Sarvam AI LLM.
        Conducts conversational clinical risk stratification by asking clarifying questions
        to evaluate condition seriousness and red flags before completing final assessment.
        """
        clean_text = transcript.strip()
        lang = language or "en-IN"
        is_hindi = lang.startswith("hi") or any("\u0900" <= ch <= "\u097F" for ch in clean_text)
        lower_text = clean_text.lower()
        has_history = bool(history and len(history) > 0)

        # Emergency red flags for safety guardrail
        critical_keywords = [
            "chest", "heart attack", "heart", "cardiac", "chest pain", "shortness of breath",
            "सीने में दर्द", "छाती में दर्द", "सीना", "छाती", "सांस फूल", "सांस लेने में", "दिल का दौरा",
            "बेहोश", "stroke", "paralysis", "लकवा", "heavy bleeding", "खून बह रहा", "poison", "ज़हर"
        ]
        is_critical_emergency = any(k in lower_text for k in critical_keywords)

        def fallback_triage() -> Dict[str, Any]:
            """Dynamic contextual fallback in case Sarvam API is unreachable."""
            if is_critical_emergency or any(k in lower_text for k in ["chest", "heart", "सीना", "छाती", "सांस"]):
                return {
                    "scenario_match": "chest",
                    "risk_assessment_status": "in_progress" if not has_history else "completed",
                    "urgency_level": "border-urgent",
                    "urgency_title": "आपातकालीन चिकित्सा परामर्श आवश्यक" if is_hindi else "Emergency Medical Care Needed",
                    "care_level": "तत्काल एम्बुलेंस 108 / नजदीकी अस्पताल" if is_hindi else "Immediate Emergency Care (Call 108)",
                    "why_matters": (
                        "सीने में तेज दर्द, भारीपन या सांस फूलना हृदय संबंधी आपातकाल का संकेत हो सकता है। इसमें समय बहुत कीमती है।"
                        if is_hindi else
                        "Chest pressure or severe breathlessness requires immediate medical evaluation to rule out cardiac emergencies."
                    ),
                    "what_to_do": (
                        "मरीज को आरामदायक स्थिति में बैठाएं। तुरंत 108 एम्बुलेंस को कॉल करें। उत्तर देने के लिए माइक का बटन दबाएं।"
                        if is_hindi else
                        "Keep patient seated comfortably. Call 108 emergency ambulance immediately. Tap mic to answer."
                    ),
                    "nearest_care": (
                        "जिला संयुक्त चिकित्सालय (DH) — 4.2 किमी (आईसीयू और 24/7 आपातकालीन सेवा)"
                        if is_hindi else
                        "District Combined Hospital (DH) — 4.2 km (ICU & 24/7 Emergency on duty)"
                    ),
                    "ai_response_speech": (
                        "कृपया तुरंत बैठ जाएं और आराम करें। स्थिति की गंभीरता समझने के लिए कृपया माइक दबाकर बताएं: क्या यह दर्द बाएं हाथ में जा रहा है और बहुत पसीना आ रहा है? तुरंत 108 एम्बुलेंस से संपर्क करें।"
                        if is_hindi else
                        "Please sit down and rest immediately. To assess urgency, please tap the mic and answer: is pain radiating to your left arm with cold sweats? Call 108 ambulance now."
                    ),
                    "follow_up_questions": [],
                    "suggested_answers": []
                }
            elif any(k in lower_text for k in ["fever", "temperature", "chills", "बुखार", "ताप", "ठंड"]):
                return {
                    "scenario_match": "fever",
                    "risk_assessment_status": "in_progress" if not has_history else "completed",
                    "urgency_level": "border-mild" if not has_history else "border-moderate",
                    "urgency_title": "बुखार गंभीरता जांच" if not has_history else "प्राथमिक स्वास्थ्य केंद्र परामर्श",
                    "care_level": "आवाज़ से उत्तर दें" if not has_history else "24-48 घंटे में डॉक्टर से मिलें",
                    "why_matters": (
                        "बुखार के साथ ठंड, सांस की तकलीफ या दाने गंभीर संक्रमण (मलेरिया/डेंगू) का संकेत हो सकते हैं।"
                        if is_hindi else
                        "Fever accompanied by chills or rash requires clinical screening to rule out acute infections."
                    ),
                    "what_to_do": (
                        "माइक का बटन दबाकर बोलें और बताएं कि बुखार कब से है। ओआरएस और पानी पिएं।"
                        if is_hindi else
                        "Tap the microphone orb to answer by voice. Stay hydrated with ORS."
                    ),
                    "nearest_care": (
                        "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी"
                        if is_hindi else
                        "Primary Health Centre (PHC) Shivpur — 1.8 km"
                    ),
                    "ai_response_speech": (
                        "बुखार की गंभीरता और जोखिम समझने के लिए कृपया माइक दबाकर बताएं: यह बुखार कितने दिनों से है और क्या तेज कंपकंपी या शरीर पर दाने हैं?"
                        if is_hindi else
                        "To evaluate the seriousness of your fever, please tap the mic and tell me: how many days have you had it, and do you have chills or a rash?"
                    ),
                    "follow_up_questions": [],
                    "suggested_answers": []
                }
            elif any(k in lower_text for k in ["stomach", "vomit", "loose", "diarrhea", "belly", "पेट", "उल्टी", "दस्त", "मरोड़"]):
                return {
                    "scenario_match": "stomach_pain",
                    "risk_assessment_status": "in_progress" if not has_history else "completed",
                    "urgency_level": "border-moderate",
                    "urgency_title": "पेट दर्द जोखिम मूल्यांकन" if not has_history else "पेट दर्द व पाचन परामर्श",
                    "care_level": "आवाज़ से उत्तर दें" if not has_history else "24 घंटे में क्लिनिक परामर्श",
                    "why_matters": (
                        "पेट दर्द के साथ उल्टी या खून आना संक्रमण या आंतरिक समस्या का जोखिम हो सकता है।"
                        if is_hindi else
                        "Abdominal pain with vomiting or fever can indicate acute infection or dehydration risk."
                    ),
                    "what_to_do": (
                        "माइक दबाकर अपने लक्षणों के बारे में बोलकर बताएं। थोड़ा-थोड़ा ओआरएस घोल पिएं।"
                        if is_hindi else
                        "Tap the mic orb and speak your answer. Sip ORS solution regularly."
                    ),
                    "nearest_care": (
                        "सामुदायिक स्वास्थ्य केंद्र (CHC) मोहनलालगंज — 3.1 किमी"
                        if is_hindi else
                        "Community Health Centre (CHC) Mohanlalganj — 3.1 km"
                    ),
                    "ai_response_speech": (
                        "पेट दर्द की गंभीरता समझने के लिए कृपया माइक दबाकर बताएं: क्या दर्द अचानक बहुत तेज हुआ या धीरे-धीरे? क्या उल्टी या बुखार भी है?"
                        if is_hindi else
                        "To understand the seriousness of your stomach pain, please tap the mic and tell me: did it start suddenly, and do you have vomiting or fever?"
                    ),
                    "follow_up_questions": [],
                    "suggested_answers": []
                }
            elif any(k in lower_text for k in ["headache", "head", "सिरदर्द", "सर दर्द", "सिर"]):
                return {
                    "scenario_match": "headache",
                    "risk_assessment_status": "in_progress" if not has_history else "completed",
                    "urgency_level": "border-mild" if not has_history else "border-moderate",
                    "urgency_title": "सिरदर्द गंभीरता जांच" if not has_history else "सिरदर्द देखभाल परामर्श",
                    "care_level": "आवाज़ से उत्तर दें" if not has_history else "घरेलू देखभाल व सामान्य क्लिनिक",
                    "why_matters": (
                        "सिरदर्द के साथ उल्टी, गर्दन में अकड़न या चक्कर आना गंभीर अंदरूनी दबाव का संकेत हो सकता है।"
                        if is_hindi else
                        "Headaches accompanied by vomiting, stiff neck, or visual changes require risk screening."
                    ),
                    "what_to_do": (
                        "माइक का बटन दबाकर बोलकर बताएं ताकि गंभीरता का सही पता चल सके।"
                        if is_hindi else
                        "Tap the mic orb and answer by voice to help evaluate risk."
                    ),
                    "nearest_care": (
                        "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी"
                        if is_hindi else
                        "Primary Health Centre (PHC) Shivpur — 1.8 km"
                    ),
                    "ai_response_speech": (
                        "सिरदर्द की गंभीरता समझने के लिए कृपया माइक दबाकर बताएं: क्या आपको उल्टी, आंखों में धुंधलापन या गर्दन में अकड़न भी है? क्या दर्द अचानक बहुत तेज हुआ?"
                        if is_hindi else
                        "To determine how serious your headache is, please tap the mic and tell me: do you have vomiting, blurry vision, or a stiff neck? Did it start suddenly?"
                    ),
                    "follow_up_questions": [],
                    "suggested_answers": []
                }
            else:
                return {
                    "scenario_match": "general_health",
                    "risk_assessment_status": "in_progress" if not has_history else "completed",
                    "urgency_level": "border-mild",
                    "urgency_title": "स्वास्थ्य गंभीरता जांच",
                    "care_level": "आवाज़ से उत्तर दें",
                    "why_matters": (
                        "लक्षणों की गंभीरता और जोखिम की सही पहचान के लिए कुछ विवरण समझना जरूरी है।"
                        if is_hindi else
                        "Clarifying symptom duration and warning signs is essential to determine clinical risk."
                    ),
                    "what_to_do": (
                        "माइक का बटन दबाकर बोलें ताकि स्थिति की गंभीरता स्पष्ट हो सके।"
                        if is_hindi else
                        "Tap the mic orb and answer by voice to assess severity."
                    ),
                    "nearest_care": "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी",
                    "ai_response_speech": (
                        f"आपकी स्थिति की गंभीरता और सही जोखिम समझने के लिए कृपया माइक दबाकर बताएं: यह परेशानी कब से है और क्या इसके साथ बुखार या कोई अन्य गंभीर तकलीफ है?"
                        if is_hindi else
                        f"To assess how serious this condition is, please tap the mic and tell me: how long have you had this, and do you have fever or any severe discomfort?"
                    ),
                    "follow_up_questions": [],
                    "suggested_answers": []
                }

        chosen_model = self._resolve_model(model, settings.SARVAM_MODEL_FALLBACK)
        messages = build_triage_messages(clean_text, language_hint=lang, history=history)

        raw_data = self._call_sarvam_with_retry(
            messages=messages,
            target_model=chosen_model,
            operation_name="triage-patient-query",
            fallback_factory=fallback_triage,
            max_tokens=600,
            temperature=0.2
        )

        # Validate and sanitize all expected fields
        scenario_match = str(raw_data.get("scenario_match") or "general_health").strip().lower()
        if any(k in lower_text for k in ["chest", "heart", "सीना", "छाती"]):
            scenario_match = "chest"
        elif any(k in lower_text for k in ["fever", "temperature", "बुखार", "ताप"]):
            scenario_match = "fever"

        urgency_level = str(raw_data.get("urgency_level") or "border-mild").strip()
        if urgency_level not in {"border-urgent", "border-moderate", "border-mild"}:
            urgency_level = "border-urgent" if is_critical_emergency else "border-moderate"

        # Safety rule override: life-threatening emergency must be border-urgent
        if is_critical_emergency:
            urgency_level = "border-urgent"

        risk_status = str(raw_data.get("risk_assessment_status") or ("completed" if has_history else "in_progress")).strip().lower()
        if risk_status not in {"in_progress", "completed"}:
            risk_status = "completed" if has_history else "in_progress"

        urgency_title = str(raw_data.get("urgency_title") or ("चिकित्सा परामर्श" if is_hindi else "Medical Guidance")).strip()
        care_level = str(raw_data.get("care_level") or ("क्लिनिक परामर्श" if is_hindi else "Clinic Consultation")).strip()
        why_matters = str(raw_data.get("why_matters") or "").strip()
        what_to_do = str(raw_data.get("what_to_do") or "").strip()
        nearest_care = str(raw_data.get("nearest_care") or ("प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी" if is_hindi else "Primary Health Centre (PHC) Shivpur — 1.8 km")).strip()
        ai_response_speech = str(raw_data.get("ai_response_speech") or "").strip()

        raw_questions = raw_data.get("follow_up_questions", [])
        follow_up_questions = [str(q).strip() for q in raw_questions if str(q).strip()] if isinstance(raw_questions, list) else []

        raw_answers = raw_data.get("suggested_answers", [])
        suggested_answers = [str(a).strip() for a in raw_answers if str(a).strip()] if isinstance(raw_answers, list) else []

        if not ai_response_speech:
            fb = fallback_triage()
            ai_response_speech = fb["ai_response_speech"]
            if not why_matters: why_matters = fb["why_matters"]
            if not what_to_do: what_to_do = fb["what_to_do"]
            if not follow_up_questions: follow_up_questions = fb["follow_up_questions"]
            if not suggested_answers: suggested_answers = fb["suggested_answers"]

        if not why_matters:
            why_matters = (
                "लक्षणों की शुरुआत और खतरे के संकेतों को जानकर ही डॉक्टर या एआई सही चिकित्सीय गंभीरता का निर्धारण कर सकते हैं।"
                if is_hindi else
                "Evaluating symptom onset and red flag warning signs is essential to determine clinical severity and risk."
            )

        return {
            "transcript": clean_text,
            "language": "hi-IN" if is_hindi else "en-IN",
            "scenario_match": scenario_match,
            "urgency_level": urgency_level,
            "urgency_title": urgency_title,
            "care_level": care_level,
            "why_matters": why_matters,
            "what_to_do": what_to_do,
            "nearest_care": nearest_care,
            "ai_response_speech": ai_response_speech,
            "risk_assessment_status": risk_status,
            "follow_up_questions": follow_up_questions,
            "suggested_answers": suggested_answers
        }


# Singleton instance for Sarvam reasoning
sarvam_reasoning_service = SarvamReasoningService()
