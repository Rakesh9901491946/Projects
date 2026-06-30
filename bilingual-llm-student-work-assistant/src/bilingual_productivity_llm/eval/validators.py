from __future__ import annotations

import re

from bilingual_productivity_llm.common.schemas import NoteToStructureExample, ValidationResult
from bilingual_productivity_llm.common.tasks import TASK_SCHEMAS
from bilingual_productivity_llm.tune.dataset import load_examples


def load_gold_examples(path: str) -> list[NoteToStructureExample]:
    return load_examples(path)


def _ordered_section_positions(text: str, sections: list[str]) -> list[int]:
    positions: list[int] = []
    for section in sections:
        positions.append(text.find(f"## {section}"))
    return positions


def _extract_output_entities(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9\-]+\b", text)
    ignore = {"Title", "Topic", "Summary", "References", "Overview", "Progress", "Context"}
    return [candidate for candidate in candidates if candidate not in ignore]


def validate_example(example: NoteToStructureExample) -> ValidationResult:
    expected_sections = TASK_SCHEMAS.get(example.task, example.required_sections)
    missing_sections = [
        section for section in expected_sections if f"## {section}" not in example.target
    ]
    supported_facts = [fact for fact in example.key_facts if fact.lower() in example.target.lower()]
    citation_present = "## References" in example.target and ("(" in example.target or "-" in example.target)
    positions = _ordered_section_positions(example.target, expected_sections)
    positioned = [position for position in positions if position >= 0]
    section_order_ok = positioned == sorted(positioned)
    output_entities = _extract_output_entities(example.target)
    unsupported = [
        entity for entity in output_entities
        if entity.lower() not in example.notes.lower() and entity.lower() not in " ".join(example.key_facts).lower()
    ]
    coverage = len(supported_facts) / len(example.key_facts) if example.key_facts else 1.0
    warnings: list[str] = []
    if not section_order_ok:
        warnings.append("Section order differs from schema.")
    if coverage < 0.8:
        warnings.append("Key fact coverage is below the desired threshold.")
    if unsupported:
        warnings.append("Potential unsupported entities detected in output.")
    return ValidationResult(
        example_id=example.example_id,
        schema_ok=not missing_sections,
        missing_sections=missing_sections,
        section_order_ok=section_order_ok,
        key_fact_coverage=coverage,
        citation_present=citation_present,
        unsupported_output_facts=unsupported,
        warnings=warnings,
    )


def run_gold_evaluation(examples: list[NoteToStructureExample]) -> list[ValidationResult]:
    return [validate_example(example) for example in examples]
