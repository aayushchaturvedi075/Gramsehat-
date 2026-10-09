"""
Layer 4 Prompts Module: Decoupled prompt templates for Sarvam AI LLM Reasoning.
"""

from app.prompts.symptom_prompts import (
    build_symptom_structuring_prompt,
    build_symptom_structuring_messages,
    SYMPTOM_STRUCTURING_SYSTEM_PROMPT,
)
from app.prompts.report_prompts import (
    build_report_explanation_prompt,
    build_report_explanation_messages,
    REPORT_EXPLANATION_SYSTEM_PROMPT,
)
from app.prompts.hospital_prompts import (
    build_hospital_summary_prompt,
    build_hospital_summary_messages,
    HOSPITAL_SUMMARY_SYSTEM_PROMPT,
)
from app.prompts.triage_prompts import (
    build_triage_prompt,
    build_triage_messages,
    TRIAGE_SYSTEM_PROMPT,
)

__all__ = [
    "build_symptom_structuring_prompt",
    "build_symptom_structuring_messages",
    "SYMPTOM_STRUCTURING_SYSTEM_PROMPT",
    "build_report_explanation_prompt",
    "build_report_explanation_messages",
    "REPORT_EXPLANATION_SYSTEM_PROMPT",
    "build_hospital_summary_prompt",
    "build_hospital_summary_messages",
    "HOSPITAL_SUMMARY_SYSTEM_PROMPT",
    "build_triage_prompt",
    "build_triage_messages",
    "TRIAGE_SYSTEM_PROMPT",
]
