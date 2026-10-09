"""
Router for Layer 4: AI Reasoning Endpoints.
Integrates Sarvam AI LLM (Sarvam-30B and Sarvam-105B) via OpenAI-compatible API
to provide structured symptoms, plain-language report explanations,
and SBAR hospital clinical handover summaries for GramSehat.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.reasoning import (
    SymptomStructureRequest,
    SymptomStructureResponse,
    ReportExplanationRequest,
    ReportExplanationResponse,
    HospitalSummaryRequest,
    HospitalSummaryResponse,
)
from app.schemas.error import ErrorResponse
from app.services.sarvam_reasoning_service import sarvam_reasoning_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Layer 4: AI Reasoning (Sarvam AI)"])


@router.post(
    "/structure-symptoms",
    response_model=SymptomStructureResponse,
    status_code=status.HTTP_200_OK,
    summary="Structure informal symptoms into clinical entities (Sarvam-30B)",
    description=(
        "Takes informal, conversational Hindi, Hinglish, or English patient speech/transcript "
        "and extracts discrete clinical symptoms, duration, severity notes, and a follow-up question. "
        "Speed-critical: utilizes Sarvam-30B (or configured fallback) for live interaction."
    ),
    responses={
        200: {
            "model": SymptomStructureResponse,
            "description": "Symptoms structured successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Empty or invalid symptom text provided."
        },
        500: {
            "model": ErrorResponse,
            "description": "AI Reasoning model error or API failure."
        }
    }
)
async def structure_symptoms(payload: SymptomStructureRequest) -> SymptomStructureResponse:
    """Parses informal rural patient symptom descriptions into structured clinical data."""
    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symptom text is empty. Please provide patient description."
        )

    try:
        response = sarvam_reasoning_service.structure_symptoms(
            text=clean_text,
            language=payload.language,
            model=payload.model
        )
        return response
    except Exception as exc:
        logger.exception("Error in /structure-symptoms: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom structuring failed: {str(exc)}"
        )


@router.post(
    "/explain-report",
    response_model=ReportExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain lab reports or prescriptions to rural patients (Sarvam-105B)",
    description=(
        "Takes OCR-extracted text from prescriptions or lab reports and explains them "
        "in plain, compassionate language (strictly 3 to 5 sentences max) with simple analogies. "
        "Identifies flagged abnormal metrics. Accuracy-critical: utilizes Sarvam-105B."
    ),
    responses={
        200: {
            "model": ReportExplanationResponse,
            "description": "Report explained successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Empty report text provided."
        },
        500: {
            "model": ErrorResponse,
            "description": "AI Reasoning model error or API failure."
        }
    }
)
async def explain_report(payload: ReportExplanationRequest) -> ReportExplanationResponse:
    """Translates medical reports/prescriptions into plain language and extracts flagged values."""
    clean_text = payload.report_text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report text is empty. Please provide valid OCR report text."
        )

    try:
        response = sarvam_reasoning_service.explain_report(
            report_text=clean_text,
            patient_query=payload.patient_query,
            screening_context=payload.screening_context,
            language=payload.language or "en",
            model=payload.model
        )
        return response
    except Exception as exc:
        logger.exception("Error in /explain-report: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report explanation failed: {str(exc)}"
        )


@router.post(
    "/generate-hospital-summary",
    response_model=HospitalSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate SBAR clinical handover summary for receiving hospital (Sarvam-105B)",
    description=(
        "Synthesizes patient demographics, symptoms, timeline, vitals, lab report findings, "
        "and Layer 3 image screening flags into a concise SBAR clinical handover summary "
        "formatted for receiving doctors and paramedics. Accuracy-critical: utilizes Sarvam-105B."
    ),
    responses={
        200: {
            "model": HospitalSummaryResponse,
            "description": "Hospital clinical handover summary generated successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Insufficient patient dossier provided."
        },
        500: {
            "model": ErrorResponse,
            "description": "AI Reasoning model error or API failure."
        }
    }
)
async def generate_hospital_summary(payload: HospitalSummaryRequest) -> HospitalSummaryResponse:
    """Generates a professional SBAR pre-arrival handover summary for receiving hospital staff."""
    dossier = payload.model_dump(exclude_unset=True)
    if not dossier or (not payload.symptoms and not payload.report_findings and not payload.vitals):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient patient data. At least symptoms, report findings, or vitals must be provided."
        )

    try:
        response = sarvam_reasoning_service.generate_hospital_summary(
            dossier=dossier,
            model=payload.model
        )
        return response
    except Exception as exc:
        logger.exception("Error in /generate-hospital-summary: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hospital summary generation failed: {str(exc)}"
        )
