"""
Layer 4 Service: Gemini AI Reasoning Engine.
Integrates google-genai SDK for symptom structuring, medical report explanations,
and SBAR hospital clinical handover summary generation.
"""

import json
import logging
import re
import time
from typing import Any, Dict, Optional

from google import genai
from google.genai import errors

from app.config import settings
from app.prompts import (
    build_symptom_structuring_prompt,
    build_report_explanation_prompt,
    build_hospital_summary_prompt,
)
from app.schemas.reasoning import (
    SymptomStructureResponse,
    ReportExplanationResponse,
    HospitalSummaryResponse,
)

logger = logging.getLogger(__name__)


class GeminiReasoningService:
    """
    Manages Gemini LLM interactions for Layer 4 AI Reasoning.
    Implements structured JSON generation, per-function configurable models,
    and automatic 1-retry handling for timeouts or malformed JSON.
    """

    def __init__(self):
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        """Lazy-initializes and returns the Google GenAI client."""
        if self._client is None:
            logger.info("Initializing Google GenAI client for Layer 4...")
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def _resolve_model(self, requested_model: Optional[str], default_model: str, fallback_model: str) -> str:
        """Resolves active model name with configurable defaults."""
        return requested_model or default_model or fallback_model

    def _clean_json_text(self, raw_text: str) -> str:
        """Strips accidental markdown code fences from JSON text if present."""
        text = raw_text.strip()
        # Remove ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def _call_gemini_json_with_retry(
        self,
        prompt_text: str,
        target_model: str,
        fallback_model: str,
        operation_name: str
    ) -> Dict[str, Any]:
        """
        Executes generate_content with response_mime_type="application/json".
        Applies 1 retry for API timeout, 503, 404 model retirement, or malformed JSON.
        """
        attempt = 0
        current_model = target_model
        last_error = None
        current_prompt = prompt_text

        while attempt <= settings.GEMINI_MAX_RETRIES:
            attempt += 1
            try:
                logger.info(
                    "Executing Layer 4 AI Reasoning [%s] (attempt %d/%d) using model '%s'",
                    operation_name, attempt, settings.GEMINI_MAX_RETRIES + 1, current_model
                )

                response = self.client.models.generate_content(
                    model=current_model,
                    contents=current_prompt,
                    config={
                        "response_mime_type": "application/json"
                    }
                )

                if not response or not response.text:
                    raise ValueError(f"Empty response returned from model '{current_model}'")

                cleaned_text = self._clean_json_text(response.text)
                parsed_json = json.loads(cleaned_text)

                logger.info(
                    "Layer 4 AI Reasoning [%s] succeeded on attempt %d using '%s'",
                    operation_name, attempt, current_model
                )
                return parsed_json

            except json.JSONDecodeError as jerr:
                last_error = jerr
                logger.warning(
                    "Malformed JSON from model '%s' in [%s] on attempt %d: %s",
                    current_model, operation_name, attempt, jerr
                )
                # Formulate corrective prompt for retry
                if attempt <= settings.GEMINI_MAX_RETRIES:
                    current_prompt = (
                        f"{prompt_text}\n\nCRITICAL FIX: The previous attempt output was malformed JSON "
                        f"({str(jerr)}). You MUST output ONLY 100% valid, parseable JSON conforming strictly to schema."
                    )
                    time.sleep(0.5)

            except errors.ClientError as cerr:
                last_error = cerr
                # Handle model retirement / 404 (e.g., deprecated 2.5 series) by falling back to modern cluster
                if cerr.code == 404 and current_model != fallback_model:
                    logger.warning(
                        "Model '%s' returned 404 (retired). Seamlessly switching to '%s' without consuming retry budget.",
                        current_model, fallback_model
                    )
                    current_model = fallback_model
                    attempt -= 1  # Reset attempt counter so the active model receives the full retry policy
                else:
                    logger.warning(
                        "ClientError in [%s] on attempt %d: %s",
                        operation_name, attempt, cerr
                    )
                time.sleep(0.5)

            except (errors.ServerError, errors.APIError, Exception) as gerr:
                last_error = gerr
                logger.warning(
                    "API/Network error in [%s] on attempt %d with model '%s': %s",
                    operation_name, attempt, current_model, gerr
                )
                # If experiencing 503 or transient failure, try fallback model on retry
                if current_model != fallback_model:
                    current_model = fallback_model
                time.sleep(1.0)

        # If exhausted all retries, raise runtime exception with clear detail
        logger.error(
            "Layer 4 AI Reasoning [%s] failed after %d attempts. Last error: %s",
            operation_name, attempt, last_error
        )
        raise RuntimeError(
            f"AI Reasoning failed after {attempt} attempts for {operation_name}: {str(last_error)}"
        )

    def structure_symptoms(
        self,
        text: str,
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> SymptomStructureResponse:
        """
        Speed-critical: Parses informal rural Hindi/English patient speech into structured symptoms.
        Uses Flash model by default for low-latency live interaction demo.
        """
        chosen_model = self._resolve_model(
            model,
            settings.MODEL_SYMPTOM_STRUCTURING,
            settings.MODEL_FALLBACK_FLASH
        )
        prompt = build_symptom_structuring_prompt(text, language)

        raw_data = self._call_gemini_json_with_retry(
            prompt_text=prompt,
            target_model=chosen_model,
            fallback_model=settings.MODEL_FALLBACK_FLASH,
            operation_name="structure-symptoms"
        )

        # Ensure field defaults match contract
        symptoms = raw_data.get("symptoms", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        elif not isinstance(symptoms, list):
            symptoms = [str(symptoms)]

        duration = str(raw_data.get("duration") or "Not specified")
        severity_notes = str(raw_data.get("severity_notes") or "Patient provided symptom description")
        follow_up = raw_data.get("follow_up_question")
        if follow_up and isinstance(follow_up, str):
            follow_up = follow_up.strip() or None
        else:
            follow_up = None

        return SymptomStructureResponse(
            symptoms=symptoms,
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
        Uses Pro model by default. Constrained strictly to 3-5 sentences.
        """
        chosen_model = self._resolve_model(
            model,
            settings.MODEL_REPORT_EXPLANATION,
            settings.MODEL_FALLBACK_PRO
        )
        prompt = build_report_explanation_prompt(
            report_text=report_text,
            patient_query=patient_query,
            screening_context=screening_context,
            language=language
        )

        raw_data = self._call_gemini_json_with_retry(
            prompt_text=prompt,
            target_model=chosen_model,
            fallback_model=settings.MODEL_FALLBACK_PRO,
            operation_name="explain-report"
        )

        explanation = str(raw_data.get("explanation", "")).strip()
        flagged_raw = raw_data.get("flagged_values", [])
        if not isinstance(flagged_raw, list):
            flagged_raw = []

        flagged_values = []
        for item in flagged_raw:
            if isinstance(item, dict):
                flagged_values.append({
                    "test_name": str(item.get("test_name", "Test")),
                    "value": str(item.get("value", "N/A")),
                    "reference_range": item.get("reference_range"),
                    "status": str(item.get("status", "abnormal")),
                    "simple_meaning": str(item.get("simple_meaning", "Consult your physician"))
                })

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
        Accuracy-critical: Synthesizes patient dossier into professional SBAR handover summary.
        Uses Pro model by default for high clinical fidelity.
        """
        chosen_model = self._resolve_model(
            model,
            settings.MODEL_HOSPITAL_SUMMARY,
            settings.MODEL_FALLBACK_PRO
        )
        prompt = build_hospital_summary_prompt(dossier)

        raw_data = self._call_gemini_json_with_retry(
            prompt_text=prompt,
            target_model=chosen_model,
            fallback_model=settings.MODEL_FALLBACK_PRO,
            operation_name="generate-hospital-summary"
        )

        summary_text = str(raw_data.get("summary", "")).strip()
        if not summary_text:
            summary_text = "Clinical SBAR summary generated from patient intake data."

        return HospitalSummaryResponse(summary=summary_text)


# Singleton service instance
gemini_service = GeminiReasoningService()
