from pydantic import BaseModel, Field

class OCRExtractResponse(BaseModel):
    """
    Response schema for POST /extract-report-text endpoint.
    Conforms to GramSehat Layer 2 specifications.
    """
    raw_text: str = Field(
        ...,
        description="Exact raw text extracted from the report or prescription image by EasyOCR",
        example="PARACETAMOL 500MG TAB\n1 गोली दिन में दो बार खाना खाने के बाद\nBP: 120/80 mmHg"
    )
    cleaned_text: str = Field(
        ...,
        description="Cleaned text with whitespace, linebreaks, and punctuation normalized for Layer 3 LLM reasoning",
        example="PARACETAMOL 500MG TAB\n1 गोली दिन में दो बार खाना खाने के बाद\nBP: 120/80 mmHg"
    )

    class Config:
        schema_extra = {
            "example": {
                "raw_text": "PARACETAMOL 500MG TAB\n1 गोली दिन में दो बार\nBP: 120/80",
                "cleaned_text": "PARACETAMOL 500MG TAB\n1 गोली दिन में दो बार\nBP: 120/80"
            }
        }
