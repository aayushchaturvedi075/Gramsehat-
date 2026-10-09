"""
Pydantic Schemas for Layer 4: Gemini AI Reasoning Module.
Defines structured request and response contracts for symptom structuring,
medical report explanations, and hospital handover summaries.
"""

from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Symptom Structuring (Speed-critical, Flash)
# ==============================================================================
class SymptomStructureRequest(BaseModel):
    """Request payload for structuring informal patient symptoms."""
    text: str = Field(
        ...,
        min_length=1,
        description="Informal conversational symptom description from Layer 2 (voice STT or text)",
        json_schema_extra={"example": "मुझे पिछले दो दिनों से बहुत तेज़ बुखार और सिरदर्द है।"}
    )
    language: Optional[str] = Field(
        default=None,
        description="Language hint (e.g. 'hi', 'en', 'hi-IN')",
        json_schema_extra={"example": "hi-IN"}
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override (e.g., 'gemini-2.5-flash', 'gemini-3.5-flash')"
    )


class SymptomStructureResponse(BaseModel):
    """Structured clinical output for symptoms feeding Layer 5 Safety Rules."""
    symptoms: List[str] = Field(
        ...,
        description="List of discrete clinical symptoms extracted from patient description",
        json_schema_extra={"example": ["High fever", "Headache"]}
    )
    duration: str = Field(
        ...,
        description="Extracted duration or timeline (e.g., '2 days', 'since morning')",
        json_schema_extra={"example": "2 days"}
    )
    severity_notes: str = Field(
        ...,
        description="Clinical notes detailing patient-reported intensity, progression, or functional limits",
        json_schema_extra={"example": "Patient reports fever is severe and accompanied by persistent headache"}
    )
    follow_up_question: Optional[str] = Field(
        default=None,
        description="Single empathetic follow-up question to clarify missing critical details, or null",
        json_schema_extra={"example": "क्या बुखार के साथ आपको ठंड या कंपकंपी भी महसूस हो रही है?"}
    )


# ==============================================================================
# 2. Report & Prescription Explanation (Accuracy-critical, Pro)
# ==============================================================================
class FlaggedValue(BaseModel):
    """Abnormal or noteworthy lab test value from medical reports."""
    test_name: str = Field(..., description="Name of test or biomarker", json_schema_extra={"example": "Hemoglobin (Hb)"})
    value: str = Field(..., description="Extracted numerical or qualitative value", json_schema_extra={"example": "8.2 g/dL"})
    reference_range: Optional[str] = Field(default=None, description="Standard healthy range", json_schema_extra={"example": "13.0 - 17.0 g/dL"})
    status: str = Field(..., description="Status classification (low, high, abnormal, attention)", json_schema_extra={"example": "low"})
    simple_meaning: str = Field(
        ...,
        description="Plain-language analogy or practical meaning for rural patients",
        json_schema_extra={"example": "Oxygen-carrying capacity in the blood is reduced, causing fatigue and dizziness"}
    )


class ReportExplanationRequest(BaseModel):
    """Request payload for explaining medical report or prescription OCR text."""
    report_text: str = Field(
        ...,
        min_length=1,
        description="Cleaned OCR text extracted from lab report or prescription (from Layer 2 EasyOCR)",
        json_schema_extra={"example": "COMPLETE BLOOD COUNT: Hemoglobin 8.2 g/dL, WBC 7400, Platelets 210000"}
    )
    patient_query: Optional[str] = Field(
        default=None,
        description="Optional specific question or concern from patient",
        json_schema_extra={"example": "Does this report explain why I feel dizzy?"}
    )
    screening_context: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional image screening findings from Layer 3 (e.g., conjunctival pallor score)"
    )
    language: Optional[str] = Field(
        default="en",
        description="Language for explanation ('en' for Indian English, 'hi' for Hindi)",
        json_schema_extra={"example": "en"}
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override (e.g. 'gemini-2.5-pro', 'gemini-3.8-flash')"
    )


class ReportExplanationResponse(BaseModel):
    """Plain-language explanation of medical report with flagged values."""
    explanation: str = Field(
        ...,
        description="Compassionate explanation for rural patients, strictly 3 to 5 sentences max",
        json_schema_extra={"example": "Your blood report indicates that your hemoglobin is lower than normal, which means your body has less oxygen-carrying strength. This explains why you have been feeling tired and dizzy recently. Your white blood cells and platelets are at healthy levels, so your body is fighting infections normally. With proper iron-rich food and guidance from your local doctor, your energy levels can steadily improve."}
    )
    flagged_values: List[FlaggedValue] = Field(
        default_factory=list,
        description="List of abnormal or attention-requiring metrics with plain-language explanations"
    )


# ==============================================================================
# 3. Hospital Handover Summary Generation (Accuracy-critical, Pro)
# ==============================================================================
class HospitalSummaryRequest(BaseModel):
    """Aggregated patient dossier for generating SBAR clinical handover summary."""
    patient_name: Optional[str] = Field(default="Patient", description="Patient name", json_schema_extra={"example": "Ramlal Sharma"})
    age: Optional[Union[int, str]] = Field(default=None, description="Patient age", json_schema_extra={"example": 54})
    gender: Optional[str] = Field(default=None, description="Patient gender", json_schema_extra={"example": "Male"})
    village: Optional[str] = Field(default=None, description="Village or geographic area", json_schema_extra={"example": "Shivpur Village"})
    symptoms: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Structured symptoms from Layer 4 or raw text from Layer 2",
        json_schema_extra={"example": ["Severe dizziness", "Orthostatic weakness"]}
    )
    duration: Optional[str] = Field(default=None, description="Symptom timeline", json_schema_extra={"example": "2 days"})
    severity_notes: Optional[str] = Field(default=None, description="Intake severity notes", json_schema_extra={"example": "Unable to walk unassisted"})
    vitals: Optional[dict[str, Any]] = Field(
        default=None,
        description="Recorded vitals (e.g., BP, Pulse, SpO2, Temperature)",
        json_schema_extra={"example": {"BP": "94/60 mmHg", "Pulse": "104 bpm", "SpO2": "97%"}}
    )
    report_findings: Optional[Union[str, List[Any]]] = Field(
        default=None,
        description="Key findings from recent lab reports or prescriptions",
        json_schema_extra={"example": "Hb 8.2 g/dL (low)"}
    )
    screening_flags: Optional[dict[str, Any]] = Field(
        default=None,
        description="Layer 3 image screening results",
        json_schema_extra={"example": {"conjunctival_pallor": "positive"}}
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model override (e.g. 'gemini-2.5-pro', 'gemini-3.8-flash')"
    )


class HospitalSummaryResponse(BaseModel):
    """Clinical handover summary for receiving hospital doctors and paramedics."""
    summary: str = Field(
        ...,
        description="Structured SBAR handover summary formatted for hospital physicians",
        json_schema_extra={"example": "PATIENT ID: Ramlal Sharma, 54M, Shivpur Village. SITUATION & TIMELINE: Presenting with acute exacerbation of severe dizziness and generalized weakness over 2 days. ASSESSMENT: Vitals show orthostatic hypotension (BP 94/60, HR 104 bpm, SpO2 97%). Lab investigations confirm moderate anemia with Hb 8.2 g/dL; screening noted positive conjunctival pallor. HANDOVER RECOMMENDATIONS: Monitor postural vitals, maintain fall precautions, evaluate for parenteral/oral iron supplementation, and repeat CBC on admission."}
    )
