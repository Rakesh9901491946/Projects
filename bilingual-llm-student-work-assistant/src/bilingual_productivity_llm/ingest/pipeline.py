from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bilingual_productivity_llm.common.schemas import (
    NormalizedDocument,
    SourceManifest,
    SourceRecord,
)
from bilingual_productivity_llm.clean.pipeline import normalize_text
from bilingual_productivity_llm.common.io import write_jsonl


def build_source_manifest(config_path: str | Path) -> SourceManifest:
    path = Path(config_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SourceManifest.model_validate(payload)


def iter_source_files(source: SourceRecord, workspace_root: str | Path) -> list[Path]:
    if not source.raw_dir:
        return []

    root = Path(workspace_root)
    raw_dir = Path(source.raw_dir)
    search_root = raw_dir if raw_dir.is_absolute() else root / raw_dir
    if not search_root.exists():
        return []

    allowed_extensions = {f".{suffix.lstrip('.').lower()}" for suffix in source.file_extensions}
    files = [
        path
        for path in search_root.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed_extensions
    ]
    return sorted(files)


def _extract_sections(text: str) -> list[str]:
    sections: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            sections.append(stripped.lstrip("#").strip())
    return sections


def _build_doc_id(source_id: str, relative_path: str) -> str:
    digest = hashlib.sha1(relative_path.encode("utf-8")).hexdigest()[:12]
    return f"{source_id}-{digest}"


def _build_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_source_file(
    file_path: str | Path,
    source: SourceRecord,
    workspace_root: str | Path,
) -> NormalizedDocument:
    path = Path(file_path)
    raw_text = path.read_text(encoding="utf-8")
    normalized = normalize_text(raw_text)
    root = Path(workspace_root).resolve()
    resolved = path.resolve()
    relative_path = str(resolved.relative_to(root)) if resolved.is_relative_to(root) else str(resolved)
    title = path.stem.replace("_", " ").replace("-", " ").strip().title()
    return NormalizedDocument(
        doc_id=_build_doc_id(source.id, relative_path),
        source=source.id,
        license=source.license,
        language=source.language,
        domain=source.domain,
        title=title,
        text=normalized,
        source_path=relative_path,
        checksum=_build_checksum(normalized),
        sections=_extract_sections(normalized),
        metadata={"filename": path.name},
    )


def build_normalized_documents(
    config_path: str | Path,
    workspace_root: str | Path,
) -> list[NormalizedDocument]:
    manifest = build_source_manifest(config_path)
    documents: list[NormalizedDocument] = []
    for source in manifest.sources:
        if not source.enabled:
            continue
        for file_path in iter_source_files(source, workspace_root):
            documents.append(normalize_source_file(file_path, source, workspace_root))
    return documents


def write_normalized_documents(
    documents: list[NormalizedDocument],
    output_path: str | Path,
) -> None:
    write_jsonl(documents, output_path)


def summarize_documents(documents: list[NormalizedDocument]) -> dict[str, int]:
    by_source: dict[str, int] = {}
    for document in documents:
        by_source[document.source] = by_source.get(document.source, 0) + 1
    return {
        "documents": len(documents),
        "sources": len(by_source),
        "source_breakdown": json.dumps(by_source, sort_keys=True),
    }
