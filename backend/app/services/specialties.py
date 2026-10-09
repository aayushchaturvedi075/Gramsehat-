"""
GramSehat Canonical Medical Specialties
=======================================
Single source of truth for hospital specialties across the entire platform.
Converts free-text clinical strings from Layer 5 (Rule Engine) into canonical slugs.
"""

from typing import Optional, Set

# Canonical specialty slugs (used in PostgreSQL hospitals.specialties text[])
CANONICAL_SPECIALTIES = (
    "cardiology",
    "ophthalmology",
    "obstetrics",
    "pediatrics",
    "neurology",
    "surgery",
    "general_medicine",
    "dermatology",
    "emergency"
)

CANONICAL_SPECIALTIES_SET: Set[str] = set(CANONICAL_SPECIALTIES)

# Normalization mapping from Layer 5 triage strings to canonical database slugs
SPECIALTY_MAP = {
    # Cardiology
    "cardiology": "cardiology",
    "cardio": "cardiology",
    "cardiac": "cardiology",
    "heart": "cardiology",

    # Ophthalmology
    "ophthalmology": "ophthalmology",
    "ophthalmic": "ophthalmology",
    "eye": "ophthalmology",
    "eye care": "ophthalmology",

    # Obstetrics & Gynecology
    "obstetrics": "obstetrics",
    "gynecology": "obstetrics",
    "obgyn": "obstetrics",
    "maternity": "obstetrics",
    "obstetric": "obstetrics",

    # Pediatrics
    "pediatrics": "pediatrics",
    "pediatric": "pediatrics",
    "paediatrics": "pediatrics",
    "child care": "pediatrics",

    # Neurology
    "neurology": "neurology",
    "neuro": "neurology",
    "emergency/neurology": "neurology",
    "stroke": "neurology",

    # Surgery & Trauma
    "surgery": "surgery",
    "surgical": "surgery",
    "emergency/surgery": "surgery",
    "trauma surgery": "surgery",

    # Emergency & Acute Care
    "emergency": "emergency",
    "emergency/general": "emergency",
    "casualty": "emergency",
    "critical care": "emergency",
    "trauma": "emergency",

    # General Medicine
    "general medicine": "general_medicine",
    "general_medicine": "general_medicine",
    "general medicine (blood test)": "general_medicine",
    "general physician": "general_medicine",
    "internal medicine": "general_medicine",
    "phc": "general_medicine",
    "chc": "general_medicine",

    # Dermatology
    "dermatology": "dermatology",
    "skin": "dermatology",
    "dermatologist": "dermatology",
}


def map_specialty_to_canonical(specialty_input: Optional[str]) -> Optional[str]:
    """
    Maps an arbitrary clinical specialty label from Layer 5 to a canonical slug.

    Args:
        specialty_input: Raw specialty string from rule engine (e.g. 'Cardiology',
                         'Emergency/Neurology', 'General Medicine (blood test)').

    Returns:
        Canonical specialty slug, or None if input was empty.
    """
    if not specialty_input:
        return None

    cleaned = str(specialty_input).strip().lower()

    # Direct match in canonical set
    if cleaned in CANONICAL_SPECIALTIES_SET:
        return cleaned

    # Exact dictionary match
    if cleaned in SPECIALTY_MAP:
        return SPECIALTY_MAP[cleaned]

    # Partial / substring heuristics for compound titles
    if "cardio" in cleaned or "heart" in cleaned:
        return "cardiology"
    if "ophthal" in cleaned or "eye" in cleaned:
        return "ophthalmology"
    if "obgyn" in cleaned or "obste" in cleaned or "matern" in cleaned:
        return "obstetrics"
    if "pediat" in cleaned or "child" in cleaned or "paediat" in cleaned:
        return "pediatrics"
    if "neuro" in cleaned or "stroke" in cleaned:
        return "neurology"
    if "surg" in cleaned:
        return "surgery"
    if "derma" in cleaned or "skin" in cleaned:
        return "dermatology"
    if "emerg" in cleaned or "trauma" in cleaned:
        return "emergency"
    if "general" in cleaned or "medicine" in cleaned or "physician" in cleaned:
        return "general_medicine"

    return None
