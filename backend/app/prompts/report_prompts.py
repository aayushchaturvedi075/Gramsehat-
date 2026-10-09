"""
Prompt template for Layer 4: Medical Report & Prescription Explanation (Sarvam AI LLM).
Explains laboratory results or prescription OCR text to rural patients in 3-5 sentences max,
identifying flagged values with simple, relatable analogies in natural Hindi/English mix.
"""

REPORT_EXPLANATION_SYSTEM_PROMPT = """You are an expert clinical communication specialist for GramSehat, a rural healthcare platform in India.
Your task is to review OCR-extracted text from laboratory reports or handwritten doctor prescriptions and explain them in plain, compassionate, and reassuring language (in a natural Hindi/English code-switched mix) that a rural patient and their family can immediately understand.

CRITICAL INSTRUCTIONS:
1. Provide an explanation that is STRICTLY 3 TO 5 SENTENCES MAXIMUM.
2. Use everyday, respectful language with simple analogies (e.g., explaining hemoglobin as the red energy/oxygen carrier in the blood, platelets as bandage cells).
3. Match the language tone to the patient's context (simple Hindi, Hinglish, or clear Indian English).
4. Identify flagged, abnormal, or out-of-range values in the report and explain their practical meaning.
5. If a patient query or screening context is provided, address it naturally within the 3-5 sentence explanation.
6. STRICT PROHIBITION: DO NOT decide, infer, or assign red/yellow/green urgency colors, triage ratings, or referral commands; that belongs strictly to Layer 5 Safety Rule Engine.
7. Return ONLY valid JSON conforming to the schema below. Do not include markdown code block wrappers or extraneous chatter.

REQUIRED JSON FORMAT:
{
  "explanation": "string (STRICTLY 3 to 5 sentences max, clear conversational Hindi/English mix)",
  "flagged_values": [
    {
      "test_name": "string",
      "value": "string",
      "reference_range": "string or null",
      "status": "low | high | abnormal | attention",
      "simple_meaning": "string (clear, plain-language description of what this means)"
    }
  ]
}
"""


def build_report_explanation_messages(
    report_text: str,
    patient_query: str = None,
    screening_context: dict = None,
    language: str = "en"
) -> list:
    """Builds chat completion message list for OpenAI-compatible Sarvam AI endpoint."""
    parts = []
    if language and language.startswith("hi"):
        parts.append("OUTPUT LANGUAGE: Clear, simple conversational Hindi/Hinglish (हिंदी/हिंग्लिश) suitable for rural patients.")
    else:
        parts.append("OUTPUT LANGUAGE: Simple, clear Indian English with natural phrasing.")

    if patient_query:
        parts.append(f"PATIENT CONCERN / QUERY:\n\"\"\"{patient_query.strip()}\"\"\"")

    if screening_context:
        parts.append(f"LAYER 3 SCREENING CONTEXT:\n{screening_context}")

    parts.append(f"REPORT / PRESCRIPTION OCR TEXT:\n\"\"\"{report_text.strip()}\"\"\"")
    parts.append("\nReturn strictly the JSON object:")

    return [
        {"role": "system", "content": REPORT_EXPLANATION_SYSTEM_PROMPT},
        {"role": "user", "content": "\n\n".join(parts)}
    ]


def build_report_explanation_prompt(
    report_text: str,
    patient_query: str = None,
    screening_context: dict = None,
    language: str = "en"
) -> str:
    """Builds the complete single string prompt for report explanation."""
    sections = [REPORT_EXPLANATION_SYSTEM_PROMPT]
    
    if language and language.startswith("hi"):
        sections.append("IMPORTANT: Output the explanation in clear, simple conversational Hindi/Hinglish (हिंदी).")
    else:
        sections.append("Output the explanation in simple, clear Indian English.")

    if patient_query:
        sections.append(f"\nPATIENT CONCERN / QUERY:\n\"\"\"{patient_query.strip()}\"\"\"")
        
    if screening_context:
        sections.append(f"\nLAYER 3 SCREENING CONTEXT:\n{screening_context}")

    sections.append(f"\nREPORT / PRESCRIPTION OCR TEXT:\n\"\"\"{report_text.strip()}\"\"\"\n\nGenerate the structured JSON response:")
    return "\n".join(sections)
