from __future__ import annotations

import unittest

from bilingual_productivity_llm.common.schemas import GenerationRequest, NoteToStructureExample
from bilingual_productivity_llm.common.tasks import TASK_SCHEMAS
from bilingual_productivity_llm.eval.validators import validate_example
from bilingual_productivity_llm.inference.backend import generate_structured_output


class GenerationTests(unittest.TestCase):
    def test_generation_produces_expected_sections(self) -> None:
        result = generate_structured_output(
            GenerationRequest(
                task="meeting_minutes",
                language="en",
                citation_style="apa-like",
                notes="Monday 10:00 sync. Anna reviewed data cleaning. Decision: keep pilot narrow. Next review Friday.",
            )
        )
        self.assertIn("## Decisions", result.output_text)
        self.assertIn("## References", result.output_text)

    def test_validator_flags_complete_example_as_schema_ok(self) -> None:
        generated = generate_structured_output(
            GenerationRequest(
                task="study_notes",
                language="en",
                citation_style="apa-like",
                notes="- Transformers use self-attention\n- Tokenization affects efficiency\n- Ref: Vaswani et al. 2017",
            )
        )
        example = NoteToStructureExample(
            example_id="test",
            task="study_notes",
            language="en",
            citation_style="apa-like",
            notes="- Transformers use self-attention\n- Tokenization affects efficiency\n- Ref: Vaswani et al. 2017",
            target=generated.output_text,
            key_facts=generated.extracted_key_facts,
            required_sections=TASK_SCHEMAS["study_notes"],
        )
        validation = validate_example(example)
        self.assertTrue(validation.schema_ok)
        self.assertTrue(validation.citation_present)


if __name__ == "__main__":
    unittest.main()
