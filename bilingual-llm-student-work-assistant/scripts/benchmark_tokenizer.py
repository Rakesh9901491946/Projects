from bilingual_productivity_llm.tokenize.train import run_tokenizer_benchmark, summarize_benchmark


def main() -> None:
    results = run_tokenizer_benchmark("data/eval/tokenizer_benchmark.jsonl")
    for result in results:
        print(
            f"{result.sample_id}\t{result.language}\t{result.chars_per_token}\t"
            f"{result.key_term_fragmentation}\t{result.citation_fragmentation}"
        )
    print("summary")
    for key, value in summarize_benchmark(results).items():
        print(f"{key}\t{value}")


if __name__ == "__main__":
    main()
