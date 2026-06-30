from bilingual_productivity_llm.common.schemas import GenerationRequest
from bilingual_productivity_llm.inference.backend import generate_structured_output


def main() -> None:
    request = GenerationRequest(
        task="meeting_minutes",
        language="en",
        citation_style="apa-like",
        notes="Monday 10:00 team sync. Anna and Lukas reviewed tokenizer delays. Decision: keep v1 focused on minutes and study notes. Next review Friday.",
    )
    result = generate_structured_output(request)
    print(result.output_text)


if __name__ == "__main__":
    main()
