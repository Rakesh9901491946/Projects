from bilingual_productivity_llm.ingest.pipeline import build_source_manifest


def main() -> None:
    manifest = build_source_manifest("configs/data_sources.json")
    for source in manifest.sources:
        print(f"{source.id}\t{source.language}\t{source.domain}\t{source.license}")


if __name__ == "__main__":
    main()
