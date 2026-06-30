from __future__ import annotations

import json
from pathlib import Path

from bilingual_productivity_llm.common.io import read_jsonl
from bilingual_productivity_llm.common.schemas import NoteToStructureExample


def load_examples(path: str | Path) -> list[NoteToStructureExample]:
    return read_jsonl(path, NoteToStructureExample)


def save_examples(path: str | Path, examples: list[NoteToStructureExample]) -> None:
    output = "\n".join(json.dumps(example.model_dump(), ensure_ascii=False) for example in examples)
    if output:
        output += "\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(output, encoding="utf-8")
