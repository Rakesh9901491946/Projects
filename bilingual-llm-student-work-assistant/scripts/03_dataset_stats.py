import json
from pathlib import Path
from collections import Counter

INPUT_PATH = Path("data_clean/corpus_clean.jsonl")
REPORT_PATH = Path("reports/day1_dataset_stats.md")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    total_docs = 0
    total_chars = 0
    lang_counter = Counter()
    source_counter = Counter()

    examples = []

    with INPUT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            total_docs += 1
            total_chars += len(item["text"])
            lang_counter[item["lang"]] += 1
            source_counter[item["source"]] += 1

            if len(examples) < 3:
                examples.append(item)

    avg_chars = total_chars / max(total_docs, 1)

    report = []
    report.append("# Day 1 Dataset Stats\n")

    report.append("## Summary\n")
    report.append(f"- Total documents: {total_docs}")
    report.append(f"- Total characters: {total_chars}")
    report.append(f"- Average characters per document: {avg_chars:.2f}\n")

    report.append("## Language Distribution\n")
    for lang, count in lang_counter.items():
        report.append(f"- {lang}: {count}")

    report.append("\n## Source Distribution\n")
    for source, count in source_counter.items():
        report.append(f"- {source}: {count}")

    report.append("\n## Sample Records\n")
    for i, item in enumerate(examples, start=1):
        text_preview = item["text"][:500].replace("\n", " ")
        report.append(f"\n### Example {i}")
        report.append(f"- Title: {item['title']}")
        report.append(f"- Language: {item['lang']}")
        report.append(f"- Source: {item['source']}")
        report.append(f"- Text preview: {text_preview}...")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")

    print(f"Saved report to {REPORT_PATH}")
    print("\n".join(report))


if __name__ == "__main__":
    main()