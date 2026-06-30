from bilingual_productivity_llm.tune.dataset import save_examples
from bilingual_productivity_llm.tune.synthetic import build_synthetic_examples


def main() -> None:
    source_path = "data/processed/filtered_docs_v1.jsonl"
    output_path = "data/interim/task_tune_synthetic_v1.jsonl"
    examples = build_synthetic_examples(source_path)
    save_examples(output_path, examples)
    print(f"examples\t{len(examples)}")
    print(f"output\t{output_path}")


if __name__ == "__main__":
    main()
