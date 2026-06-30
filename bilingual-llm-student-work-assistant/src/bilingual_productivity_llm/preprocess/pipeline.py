from __future__ import annotations

import json
from pathlib import Path

from bilingual_productivity_llm.clean.pipeline import build_cleaned_document, filter_cleaned_documents
from bilingual_productivity_llm.common.io import write_jsonl
from bilingual_productivity_llm.common.schemas import CleanedDocument
from bilingual_productivity_llm.dedup.pipeline import deduplicate_documents
from bilingual_productivity_llm.ingest.pipeline import build_normalized_documents


def build_preprocessed_corpus(
    config_path: str | Path,
    workspace_root: str | Path,
    minimum_quality_score: float = 0.6,
) -> list[CleanedDocument]:
    normalized = build_normalized_documents(config_path=config_path, workspace_root=workspace_root)
    cleaned = [build_cleaned_document(document) for document in normalized]
    filtered = filter_cleaned_documents(cleaned, minimum_quality_score=minimum_quality_score)
    return deduplicate_documents(filtered)


def write_preprocessed_corpus(
    documents: list[CleanedDocument],
    output_path: str | Path,
) -> None:
    write_jsonl(documents, output_path)


def build_preprocess_report(documents: list[CleanedDocument]) -> dict[str, int | float | str]:
    kept = [document for document in documents if document.kept]
    duplicates = [document for document in documents if document.duplicate_of]
    low_quality = [document for document in documents if "short_document" in document.quality_flags]
    by_language: dict[str, int] = {}
    for document in kept:
        by_language[document.primary_language] = by_language.get(document.primary_language, 0) + 1
    average_quality = round(
        sum(document.quality_score for document in kept) / len(kept), 3
    ) if kept else 0.0
    return {
        "documents_total": len(documents),
        "documents_kept": len(kept),
        "duplicates_flagged": len(duplicates),
        "short_documents_flagged": len(low_quality),
        "average_quality_score": average_quality,
        "kept_language_breakdown": json.dumps(by_language, sort_keys=True),
    }
