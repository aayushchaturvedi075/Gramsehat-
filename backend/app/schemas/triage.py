from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TranscriptRequest(BaseModel):
    """
    Request model for patient transcript text and multi-turn intake history.
    Transcribed via Sarvam AI Speech-to-Text (Saaras v3) or typed in manually.
    """
    transcript: str = Field(
        ...,
        min_length=1,
        description="Final symptom transcript captured by Sarvam AI STT or user input",
        json_schema_extra={"example": "मुझे पिछले तीन दिनों से तेज़ बुखार और सिरदर्द है।"}
    )
    language: Optional[str] = Field(
        default="en-IN",
        description="Speech recognition language code (e.g. 'en-IN', 'hi-IN')",
        json_schema_extra={"example": "hi-IN"}
    )
    history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous intake turns [{role: 'user'|'assistant', content: '...'}] for interactive risk assessment",
        json_schema_extra={"example": [{"role": "user", "content": "पेट में दर्द है"}, {"role": "assistant", "content": "क्या उल्टी भी है?"}]}
    )


class ClinicalTriageResponse(BaseModel):
    """
    Clinical triage and reasoning response returned to the frontend.
    Feeds downstream clinical assessments and generates the AI voice explanation.
    """
    transcript: str = Field(..., description="Original patient transcript text")
    language: str = Field(..., description="Language of analysis ('en-IN' or 'hi-IN')")
    scenario_match: str = Field(..., description="Matched clinical scenario category (dizziness, fever, chest, general)")
    urgency_level: str = Field(..., description="Acuity class (border-mild, border-moderate, border-urgent)")
    urgency_title: str = Field(..., description="Short clinical headline")
    care_level: str = Field(..., description="Recommended level of care (e.g. Clinic visit, Emergency care)")
    why_matters: str = Field(..., description="Plain-language clinical reason for rural patients")
    what_to_do: str = Field(..., description="Immediate practical steps to take now")
    nearest_care: str = Field(..., description="Nearest verified healthcare facility")
    ai_response_speech: str = Field(..., description="Clinical companion explanation for Web Speech TTS narration")
    risk_assessment_status: str = Field(default="in_progress", description="'in_progress' (asking clarifying questions to evaluate risk) or 'completed' (seriousness evaluated)")
    follow_up_questions: List[str] = Field(default_factory=list, description="Targeted clinical questions to assess condition severity and red flags")
    suggested_answers: List[str] = Field(default_factory=list, description="Quick tap-to-answer choices for patients")

    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "कल से चक्कर और बहुत कमजोरी लग रही है",
                "language": "hi-IN",
                "scenario_match": "dizziness",
                "urgency_level": "border-moderate",
                "urgency_title": "प्राथमिक क्लिनिक परामर्श अनुशंसित",
                "care_level": "क्लिनिक जाने की सलाह (24 घंटे के अंदर)",
                "why_matters": "चक्कर और कमजोरी शरीर में खून की कमी (एनीमिया) या निर्जलीकरण से हो सकती है।",
                "what_to_do": "ठंडी जगह पर बैठें या लेटें। पानी अथवा ओआरएस पिएं। अचानक खड़े न हों।",
                "nearest_care": "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी दूर",
                "ai_response_speech": "नमस्ते। आपके लक्षणों के अनुसार, कृपया 24 घंटे के अंदर नजदीकी प्राथमिक स्वास्थ्य केंद्र पर जाकर खून की जांच करवाएं।"
            }
        }
