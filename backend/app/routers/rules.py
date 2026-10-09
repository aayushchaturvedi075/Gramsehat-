"""
FastAPI Router for GramSehat Layer 5: Safety Rule Engine.
Exposes the deterministic clinical urgency assessment endpoint.
"""

import logging
from fastapi import APIRouter, Depends, status
from app.schemas.rules import (
    UrgencyAssessmentRequest,
    UrgencyAssessmentResponse,
)
from app.services.rule_engine import SafetyRuleEngine, get_rule_engine

logger = logging.getLogger("gramsehat.rules_router")

router = APIRouter(
    tags=["Layer 5: Safety Rule Engine (Deterministic)"]
)


@router.post(
    "/assess-urgency",
    response_model=UrgencyAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Assess Clinical Urgency (Layer 5)",
    description=(
        "Deterministic, config-driven clinical urgency assessment based on WHO/IMCI guidelines.\n\n"
        "- Evaluates structured symptoms (Layer 4), raw voice transcripts (Layer 2), and screening flags (Layer 3).\n"
        "- Employs purely fixed rules from `rules.yaml` and multi-lingual keywords from `keywords.yaml`.\n"
        "- Strictly zero LLM/ML dependencies for maximum predictability and safety.\n"
        "- Fails safe to 'yellow' for empty or uninterpretable input."
    )
)
def assess_urgency_endpoint(
    request: UrgencyAssessmentRequest,
    engine: SafetyRuleEngine = Depends(get_rule_engine)
) -> UrgencyAssessmentResponse:
    """
    Evaluate symptoms and return triage urgency (red / yellow / green),
    triggered rules, and referral specialty for Layer 8.
    """
    logger.info(
        "Processing urgency assessment: raw_text_len=%d, structured_count=%d, screening_count=%d, patient=%s",
        len(request.raw_text or ""),
        len(request.structured_symptoms or []),
        len(request.screening_flags or []),
        request.patient.model_dump() if request.patient else {}
    )

    verdict = engine.evaluate(request)

    logger.info(
        "Assessed urgency: %s | Triggered rules: %s | Specialty: %s",
        verdict.urgency,
        verdict.triggered_rules,
        verdict.required_specialty
    )
    return verdict
