"""Pydantic contract for the AI vision response."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, confloat


class AIIssue(BaseModel):
    type: Literal[
        "color_only", "icon_unclear", "missing_label",
        "small_target", "layout", "alt_text", "other",
    ]
    severity: Literal["critical", "serious", "minor"]
    box: List[confloat(ge=0, le=1)] = Field(min_length=4, max_length=4)
    description: str
    affected_users: str
    fix: str
    confidence: confloat(ge=0, le=1)


class AltText(BaseModel):
    box: List[confloat(ge=0, le=1)] = Field(min_length=4, max_length=4)
    alt: str


class AIResponse(BaseModel):
    issues: List[AIIssue] = []
    alt_texts: List[AltText] = []
    screen_reader_script: List[str] = []
