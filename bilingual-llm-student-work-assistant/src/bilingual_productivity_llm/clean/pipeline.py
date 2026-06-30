from __future__ import annotations

import re

from bilingual_productivity_llm.common.schemas import CleanedDocument, NormalizedDocument


GERMAN_HINTS = {
    "und",
    "der",
    "die",
    "das",
    "nicht",
    "mit",
    "ist",
    "wird",
    "studium",
    "wichtige",
    "dokumentation",
}
ENGLISH_HINTS = {
    "and",
    "the",
    "with",
    "this",
    "that",
    "meeting",
    "documentation",
    "summary",
    "study",
    "project",
}


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving line-oriented structure."""
    lines = [line.rstrip() for line in text.splitlines()]
    compact = "\n".join(lines)
    return "\n".join(part for part in compact.splitlines() if part.strip())


def clean_document_text(text: str) -> str:
    """Apply lightweight corpus cleaning while preserving document structure."""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    lines = [line.strip() for line in cleaned.splitlines()]
    filtered_lines = [line for line in lines if line]
    return "\n".join(filtered_lines)


def detect_language(text: str) -> tuple[str, str | None, float]:
    lower = text.lower()
    tokens = re.findall(r"[a-zA-ZäöüÄÖÜß]+", lower)
    if not tokens:
        return "mixed", None, 0.0

    german_hits = sum(token in GERMAN_HINTS or any(ch in token for ch in "äöüß") for token in tokens)
    english_hits = sum(token in ENGLISH_HINTS for token in tokens)
    total_hits = german_hits + english_hits

    if german_hits and english_hits:
        primary = "de" if german_hits >= english_hits else "en"
        secondary = "en" if primary == "de" else "de"
        confidence = max(german_hits, english_hits) / total_hits if total_hits else 0.5
        return "mixed", secondary if primary != "mixed" else None, round(confidence, 3)

    if german_hits > english_hits:
        confidence = german_hits / max(len(tokens), 1)
        return "de", None, round(min(1.0, confidence * 3), 3)

    if english_hits > german_hits:
        confidence = english_hits / max(len(tokens), 1)
        return "en", None, round(min(1.0, confidence * 3), 3)

    return "mixed", None, 0.2


def score_quality(text: str) -> tuple[float, list[str]]:
    flags: list[str] = []
    length = len(text)
    lines = text.splitlines()
    unique_lines = len(set(lines))
    repeated_line_ratio = 1.0 - (unique_lines / len(lines)) if lines else 0.0
    alphabetic = sum(char.isalpha() for char in text)
    alpha_ratio = alphabetic / length if length else 0.0
    noisy_chars = sum(not (char.isprintable() or char in "\n\t") for char in text)
    noisy_ratio = noisy_chars / length if length else 0.0

    score = 1.0
    if length < 80:
        flags.append("short_document")
        score -= 0.20
    if alpha_ratio < 0.55:
        flags.append("low_alpha_ratio")
        score -= 0.25
    if repeated_line_ratio > 0.25:
        flags.append("repeated_lines")
        score -= 0.20
    if noisy_ratio > 0.01:
        flags.append("noisy_characters")
        score -= 0.20

    return max(0.0, round(score, 3)), flags


def build_cleaned_document(document: NormalizedDocument) -> CleanedDocument:
    cleaned_text = clean_document_text(document.text)
    detected_language, secondary_language, confidence = detect_language(cleaned_text)
    quality_score, quality_flags = score_quality(cleaned_text)
    return CleanedDocument(
        doc_id=document.doc_id,
        source=document.source,
        license=document.license,
        language=document.language,
        domain=document.domain,
        title=document.title,
        text=cleaned_text,
        source_path=document.source_path,
        checksum=document.checksum,
        sections=document.sections,
        metadata=document.metadata,
        quality_score=quality_score,
        quality_flags=quality_flags,
        primary_language=detected_language,
        secondary_language=secondary_language,
        language_confidence=confidence,
    )


def filter_cleaned_documents(
    documents: list[CleanedDocument],
    minimum_quality_score: float = 0.6,
) -> list[CleanedDocument]:
    filtered: list[CleanedDocument] = []
    for document in documents:
        keep = document.quality_score >= minimum_quality_score and bool(document.text.strip())
        filtered.append(document.model_copy(update={"kept": keep}))
    return filtered
