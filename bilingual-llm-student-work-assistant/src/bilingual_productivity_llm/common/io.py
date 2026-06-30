from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel


ModelT = TypeVar("ModelT", bound=BaseModel)


def write_jsonl(records: list[BaseModel], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(record.model_dump_json() for record in records)
    if payload:
        payload += "\n"
    path.write_text(payload, encoding="utf-8")


def read_jsonl(path: str | Path, model_type: type[ModelT]) -> list[ModelT]:
    records: list[ModelT] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(model_type.model_validate(json.loads(line)))
    return records
