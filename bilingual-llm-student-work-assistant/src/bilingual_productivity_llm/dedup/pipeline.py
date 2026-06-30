from __future__ import annotations

from collections.abc import Iterable

from bilingual_productivity_llm.common.schemas import CleanedDocument


def exact_deduplicate(texts: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for text in texts:
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def deduplicate_documents(documents: list[CleanedDocument]) -> list[CleanedDocument]:
    seen_by_checksum: dict[str, str] = {}
    deduplicated: list[CleanedDocument] = []
    for document in documents:
        duplicate_of = seen_by_checksum.get(document.checksum)
        if duplicate_of:
            deduplicated.append(
                document.model_copy(update={"duplicate_of": duplicate_of, "kept": False})
            )
            continue
        seen_by_checksum[document.checksum] = document.doc_id
        deduplicated.append(document)
    return deduplicated
