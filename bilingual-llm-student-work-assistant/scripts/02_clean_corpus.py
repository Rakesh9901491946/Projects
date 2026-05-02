import json
import re
from pathlib import Path
from collections import defaultdict

INPUT_PATH = Path("data_clean/corpus_sample.jsonl")
OUTPUT_PATH = Path("data_clean/corpus_clean.jsonl")


def clean_text(text: str) -> str:
    text = text.replace("\t", " ")
    text = text.replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = text.strip()
    return text


def is_good_text(text: str) -> bool:
    if len(text) < 300:
        return False

    letters = sum(ch.isalpha() for ch in text)
    letter_ratio = letters / max(len(text), 1)

    if letter_ratio < 0.55:
        return False

    return True


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    seen = set()
    kept = 0
    skipped = defaultdict(int)

    with INPUT_PATH.open("r", encoding="utf-8") as inp, OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for line in inp:
            item = json.loads(line)

            text = clean_text(item["text"])

            if not is_good_text(text):
                skipped["low_quality"] += 1
                continue

            dedup_key = text[:1000]

            if dedup_key in seen:
                skipped["duplicate"] += 1
                continue

            seen.add(dedup_key)

            item["text"] = text

            out.write(json.dumps(item, ensure_ascii=False) + "\n")
            kept += 1

    print(f"Saved cleaned corpus to {OUTPUT_PATH}")
    print(f"Kept: {kept}")
    print(f"Skipped: {dict(skipped)}")


if __name__ == "__main__":
    main()