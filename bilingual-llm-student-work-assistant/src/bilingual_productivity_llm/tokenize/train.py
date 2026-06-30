from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

from bilingual_productivity_llm.common.io import read_jsonl
from bilingual_productivity_llm.common.schemas import TokenizerBenchmarkSample


def load_tokenizer_config(config_path: str | Path) -> dict:
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


@dataclass
class TokenizerBenchmarkResult:
    sample_id: str
    language: str
    chars_per_token: float
    key_term_fragmentation: float
    citation_fragmentation: float


def _simple_tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÄÖÜäöüß0-9]+|[^\w\s]", text)


def _fragmentation_ratio(tokens: list[str], text: str) -> float:
    words = re.findall(r"[A-Za-zÄÖÜäöüß0-9][A-Za-zÄÖÜäöüß0-9\-]*", text)
    if not words:
        return 0.0
    long_words = [word for word in words if len(word) >= 10 or "-" in word]
    if not long_words:
        return 0.0
    token_count = sum(1 for token in tokens if any(fragment.lower() in token.lower() or token.lower() in fragment.lower() for fragment in long_words))
    return round(token_count / len(long_words), 3)


def _citation_fragmentation(tokens: list[str], text: str) -> float:
    citation_like = [part for part in re.split(r"\s+", text) if "(" in part or ")" in part or "." in part]
    if not citation_like:
        return 0.0
    matched = sum(
        1
        for token in tokens
        if any(mark in token for mark in ["(", ")", ".", ";", ":"])
    )
    return round(matched / len(citation_like), 3)


def load_tokenizer_benchmark(path: str | Path) -> list[TokenizerBenchmarkSample]:
    return read_jsonl(path, TokenizerBenchmarkSample)


def run_tokenizer_benchmark(path: str | Path) -> list[TokenizerBenchmarkResult]:
    samples = load_tokenizer_benchmark(path)
    results: list[TokenizerBenchmarkResult] = []
    for sample in samples:
        tokens = _simple_tokenize(sample.text)
        chars_per_token = round(len(sample.text) / len(tokens), 3) if tokens else 0.0
        results.append(
            TokenizerBenchmarkResult(
                sample_id=sample.id,
                language=sample.language,
                chars_per_token=chars_per_token,
                key_term_fragmentation=_fragmentation_ratio(tokens, sample.text),
                citation_fragmentation=_citation_fragmentation(tokens, sample.text),
            )
        )
    return results


def summarize_benchmark(results: list[TokenizerBenchmarkResult]) -> dict[str, float]:
    if not results:
        return {
            "samples": 0.0,
            "avg_chars_per_token": 0.0,
            "avg_key_term_fragmentation": 0.0,
            "avg_citation_fragmentation": 0.0,
        }
    return {
        "samples": float(len(results)),
        "avg_chars_per_token": round(
            sum(result.chars_per_token for result in results) / len(results), 3
        ),
        "avg_key_term_fragmentation": round(
            sum(result.key_term_fragmentation for result in results) / len(results), 3
        ),
        "avg_citation_fragmentation": round(
            sum(result.citation_fragmentation for result in results) / len(results), 3
        ),
    }
