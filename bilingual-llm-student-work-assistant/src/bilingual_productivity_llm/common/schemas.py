from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


Language = Literal["de", "en", "mixed"]
TaskType = Literal[
    "meeting_minutes",
    "project_report",
    "study_notes",
    "professional_summary",
]


class SourceRecord(BaseModel):
    id: str
    language: Language
    domain: str
    license: str
    enabled: bool = True
    notes: str = ""
    raw_dir: Optional[str] = None
    file_extensions: list[str] = Field(default_factory=lambda: ["txt", "md"])


class SourceManifest(BaseModel):
    version: int = Field(ge=1)
    sources: list[SourceRecord]


class NormalizedDocument(BaseModel):
    doc_id: str
    source: str
    license: str
    language: Language
    domain: str
    title: str
    text: str
    source_path: str
    checksum: str
    acquisition_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).date().isoformat()
    )
    sections: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CleanedDocument(BaseModel):
    doc_id: str
    source: str
    license: str
    language: Language
    domain: str
    title: str
    text: str
    source_path: str
    checksum: str
    sections: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    quality_score: float = Field(ge=0.0, le=1.0)
    quality_flags: list[str] = Field(default_factory=list)
    primary_language: Language
    secondary_language: Optional[Language] = None
    language_confidence: float = Field(ge=0.0, le=1.0)
    duplicate_of: Optional[str] = None
    kept: bool = True


class NoteToStructureExample(BaseModel):
    example_id: str
    task: TaskType
    language: Language
    citation_style: str
    notes: str
    target: str
    key_facts: list[str]
    required_sections: list[str]


class TokenizerBenchmarkSample(BaseModel):
    id: str
    language: Language
    text: str


class GenerationRequest(BaseModel):
    task: TaskType
    language: Language
    citation_style: str
    notes: str
    strict_structure: bool = True


class GenerationResult(BaseModel):
    task: TaskType
    language: Language
    output_text: str
    extracted_key_facts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    example_id: str
    schema_ok: bool
    missing_sections: list[str]
    section_order_ok: bool = True
    key_fact_coverage: float
    citation_present: bool
    unsupported_output_facts: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
