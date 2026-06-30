from bilingual_productivity_llm.eval.validators import load_gold_examples, run_gold_evaluation


def main() -> None:
    examples = load_gold_examples("data/eval/gold_examples.jsonl")
    results = run_gold_evaluation(examples)
    for result in results:
        print(result.model_dump_json())


if __name__ == "__main__":
    main()

