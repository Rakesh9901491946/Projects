from datasets import load_dataset
from pathlib import Path
import json

OUTPUT_DIR = Path("data_clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "corpus_sample.jsonl"

MAX_EN = 1000
MAX_DE = 1000


def write_jsonl(records, output_path):
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    records = []

    print("Loading lightweight English sample from Wikitext...")

    en_dataset = load_dataset(
        "wikitext",
        "wikitext-2-raw-v1",
        split="train"
    )

    en_count = 0

    for i, item in enumerate(en_dataset):
        text = item.get("text", "").strip()

        if len(text) < 300:
            continue

        records.append({
            "title": f"wikitext_en_{i}",
            "text": text,
            "lang": "en",
            "source": "wikitext_2_raw"
        })

        en_count += 1

        if en_count >= MAX_EN:
            break

    print(f"Collected English records: {en_count}")

    print("Creating German seed corpus for MVP...")

    german_seed_texts = [
        """
        Dieses Projekt untersucht die Entwicklung eines bilingualen Sprachmodells für deutsche und englische Texte.
        Ziel ist es, unstrukturierte Notizen in klare Berichte, Zusammenfassungen und Besprechungsprotokolle umzuwandeln.
        Der Fokus liegt auf studentischer und beruflicher Produktivität.
        """,
        """
        Studierende und Mitarbeitende verbringen häufig viel Zeit mit dem Schreiben, Strukturieren und Überarbeiten von Texten.
        Ein spezialisiertes Sprachmodell kann helfen, Notizen in eine klare Struktur zu bringen.
        Dazu gehören Projektberichte, Lernnotizen, professionelle Zusammenfassungen und Meeting-Protokolle.
        """,
        """
        Die Datenpipeline umfasst Datensammlung, Textbereinigung, Deduplizierung und Qualitätsfilterung.
        Danach wird ein eigener Tokenizer trainiert.
        Anschließend wird ein kleines Sprachmodell von Grund auf vortrainiert und für strukturierte Aufgaben angepasst.
        """,
        """
        Die Evaluation konzentriert sich auf drei zentrale Aspekte.
        Erstens wird geprüft, ob das Ausgabeformat korrekt ist.
        Zweitens wird bewertet, ob wichtige Fakten aus den Notizen erhalten bleiben.
        Drittens wird die sprachliche Qualität in Deutsch und Englisch geprüft.
        """,
        """
        In einem praktischen Anwendungsfall gibt eine Nutzerin unstrukturierte Stichpunkte ein.
        Das System erzeugt daraus eine strukturierte Zusammenfassung mit klaren Überschriften.
        Für berufliche Szenarien kann das Modell Entscheidungen, Aufgaben und Verantwortlichkeiten aus Meeting-Notizen ableiten.
        """
    ]

    de_count = 0

    for i in range(MAX_DE):
        base_text = german_seed_texts[i % len(german_seed_texts)].strip()

        text = (
            base_text
            + "\n\n"
            + "Dieses Beispiel wird für den Aufbau eines kleinen deutschen Trainingskorpus verwendet. "
            + "Es dient als erster MVP-Datensatz, bevor größere offene Datenquellen integriert werden."
        )

        records.append({
            "title": f"german_seed_{i}",
            "text": text,
            "lang": "de",
            "source": "german_seed_mvp"
        })

        de_count += 1

    print(f"Collected German records: {de_count}")

    write_jsonl(records, OUTPUT_PATH)

    print(f"Saved total records: {len(records)}")
    print(f"Output file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()