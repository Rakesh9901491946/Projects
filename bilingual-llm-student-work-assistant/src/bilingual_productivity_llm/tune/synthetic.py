from __future__ import annotations

from pathlib import Path

from bilingual_productivity_llm.common.io import read_jsonl
from bilingual_productivity_llm.common.schemas import CleanedDocument, NoteToStructureExample
from bilingual_productivity_llm.common.tasks import TASK_SCHEMAS
from bilingual_productivity_llm.inference.backend import generate_structured_output
from bilingual_productivity_llm.common.schemas import GenerationRequest


DEFAULT_TASK_SEQUENCE = [
    "meeting_minutes",
    "study_notes",
    "project_report",
    "professional_summary",
]


def build_note_style_input(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    notes: list[str] = []
    for line in lines[:4]:
        stripped = line.lstrip("#").strip()
        if not stripped:
            continue
        notes.append(f"- {stripped}")
    return "\n".join(notes)


def build_synthetic_examples(
    corpus_path: str | Path,
    citation_style: str = "apa-like",
) -> list[NoteToStructureExample]:
    documents = read_jsonl(corpus_path, CleanedDocument)
    examples: list[NoteToStructureExample] = []
    for index, document in enumerate(documents):
        task = DEFAULT_TASK_SEQUENCE[index % len(DEFAULT_TASK_SEQUENCE)]
        notes = build_note_style_input(document.text)
        generation = generate_structured_output(
            GenerationRequest(
                task=task,
                language=document.primary_language,
                citation_style=citation_style,
                notes=notes,
            )
        )
        examples.append(
            NoteToStructureExample(
                example_id=f"synthetic_{task}_{index+1:03d}",
                task=task,
                language=document.primary_language,
                citation_style=citation_style,
                notes=notes,
                target=generation.output_text,
                key_facts=generation.extracted_key_facts,
                required_sections=TASK_SCHEMAS[task],
            )
        )
    return examples
