from bilingual_productivity_llm.ingest.pipeline import (
    build_normalized_documents,
    summarize_documents,
    write_normalized_documents,
)


def main() -> None:
    config_path = "configs/data_sources.json"
    output_path = "data/processed/normalized_docs_v1.jsonl"
    documents = build_normalized_documents(config_path=config_path, workspace_root=".")
    write_normalized_documents(documents, output_path)
    summary = summarize_documents(documents)
    for key, value in summary.items():
        print(f"{key}\t{value}")


if __name__ == "__main__":
    main()
