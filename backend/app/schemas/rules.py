"""
Pydantic schemas for GramSehat Layer 5: Safety Rule Engine.
Defines strict validation for assessment requests and structured verdicts.
"""

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


class PatientContext(BaseModel):
    """Demographic and physiological risk factors."""
    age: Optional[Union[float, int]] = Field(
        default=None,
        description="Patient age in years (e.g. 0.5 for 6 months, 4 for 4 years, 65 for elderly)",
        ge=0,
        le=130
    )
    is_pregnant: Optional[bool] = Field(
        default=False,
        description="Whether the patient is currently pregnant"
    )

    @field_validator("age", mode="before")
    @classmethod
    def parse_age(cls, v):
        if v is None or v == "":
            return None
        try:
            val = float(v)
            return max(0.0, val)
        except (ValueError, TypeError):
            return None

    @field_validator("is_pregnant", mode="before")
    @classmethod
    def parse_pregnancy(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() in ("true", "1", "yes", "t", "y")
        if isinstance(v, (int, float)):
            return bool(v)
        return False


class UrgencyAssessmentRequest(BaseModel):
    """
    Request payload for Layer 5 Safety Rule Engine.
    Combines Layer 4 structured symptoms, Layer 2 raw text transcript,
    and Layer 3 image screening flags.
    """
    structured_symptoms: Optional[List[str]] = Field(
        default_factory=list,
        description="Clinical symptom tags or phrases extracted by Layer 4 AI",
        json_schema_extra={"example": ["chest_pain", "breathlessness"]}
    )
    raw_text: Optional[str] = Field(
        default="",
        description="Raw transcribed user speech in Hindi, English, or Hinglish from Layer 2",
        json_schema_extra={"example": "सीने में बहुत तेज दर्द है और सांस लेने में दिक्कत हो रही है"}
    )
    screening_flags: Optional[List[str]] = Field(
        default_factory=list,
        description="Computer vision screening indicators from Layer 3 (e.g. pallor_screening_flag)",
        json_schema_extra={"example": ["pallor_screening_flag"]}
    )
    patient: Optional[PatientContext] = Field(
        default_factory=PatientContext,
        description="Demographic risk modifiers (age, pregnancy status)"
    )

    @field_validator("structured_symptoms", "screening_flags", mode="before")
    @classmethod
    def ensure_list_of_strings(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if item is not None and str(item).strip()]
        return []

    @field_validator("raw_text", mode="before")
    @classmethod
    def ensure_string(cls, v):
        if v is None:
            return ""
        return str(v)


class UrgencyAssessmentResponse(BaseModel):
    """
    Urgency assessment response returned by Layer 5.
    Directly consumable by Layer 8 (Hospital Matching) and Layer 7 (Database Logging).
    """
    urgency: Literal["red", "yellow", "green"] = Field(
        ...,
        description="Clinical triage tier: 'red' (Emergency), 'yellow' (Clinic Visit within 24h), 'green' (Supportive Home Care)"
    )
    triggered_rules: List[str] = Field(
        default_factory=list,
        description="Identifiers of all deterministic clinical rules that triggered"
    )
    reason: str = Field(
        ...,
        description="Explainable, plain-language clinical justification for the assigned urgency"
    )
    recommended_action: str = Field(
        ...,
        description="Immediate actionable guidance for patient, ASHA worker, or transport dispatcher"
    )
    required_specialty: Optional[str] = Field(
        default=None,
        description="Target clinical medical specialty required for referral (e.g., Cardiology, Obstetrics, Pediatrics)"
    )
    follow_up_question: Optional[str] = Field(
        default=None,
        description="Clarifying clinical query to guide patient dialogue when input was ambiguous or needs refinement"
    )
