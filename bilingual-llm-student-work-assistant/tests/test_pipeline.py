from __future__ import annotations

import unittest

from bilingual_productivity_llm.common.io import read_jsonl
from bilingual_productivity_llm.common.schemas import CleanedDocument, NormalizedDocument
from bilingual_productivity_llm.tune.synthetic import build_synthetic_examples


class PipelineTests(unittest.TestCase):
    def test_normalized_artifact_is_readable(self) -> None:
        documents = read_jsonl("data/processed/normalized_docs_v1.jsonl", NormalizedDocument)
        self.assertGreaterEqual(len(documents), 4)
        self.assertTrue(all(document.doc_id for document in documents))

    def test_preprocessed_artifact_keeps_quality_fields(self) -> None:
        documents = read_jsonl("data/processed/filtered_docs_v1.jsonl", CleanedDocument)
        self.assertGreaterEqual(len(documents), 4)
        self.assertTrue(all(document.quality_score >= 0.0 for document in documents))
        self.assertTrue(all(document.primary_language in {"de", "en", "mixed"} for document in documents))

    def test_synthetic_examples_are_generated(self) -> None:
        examples = build_synthetic_examples("data/processed/filtered_docs_v1.jsonl")
        self.assertGreaterEqual(len(examples), 4)
        self.assertTrue(all(example.required_sections for example in examples))


if __name__ == "__main__":
    unittest.main()
