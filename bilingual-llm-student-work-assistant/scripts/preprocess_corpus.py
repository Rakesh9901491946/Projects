from bilingual_productivity_llm.preprocess.pipeline import (
    build_preprocess_report,
    build_preprocessed_corpus,
    write_preprocessed_corpus,
)


def main() -> None:
    config_path = "configs/data_sources.json"
    output_path = "data/processed/filtered_docs_v1.jsonl"
    documents = build_preprocessed_corpus(
        config_path=config_path,
        workspace_root=".",
        minimum_quality_score=0.6,
    )
    write_preprocessed_corpus(documents, output_path)
    report = build_preprocess_report(documents)
    for key, value in report.items():
        print(f"{key}\t{value}")


if __name__ == "__main__":
    main()
