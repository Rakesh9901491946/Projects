# Bilingual DE/EN Productivity LLM

This repository scaffolds an end-to-end pipeline for training a bilingual German-English, domain-specific language model from scratch for structured productivity writing.

Primary target tasks:

- meeting minutes
- project reports
- study notes
- professional summaries

The initial scaffold focuses on:

- reproducible data contracts
- schema-aware task examples
- evaluation validators
- a Streamlit demo shell with inference and validation wiring
- starter ingestion pipeline for raw text and markdown corpora
- preprocessing with cleaning, quality scoring, and exact deduplication
- tokenizer benchmarking utilities
- a reusable inference backend interface

## Repository Layout

```text
configs/          Experiment and pipeline configuration
data/             Manifests and evaluation samples
scripts/          Thin CLI entrypoints
src/              Python package code
app/              Streamlit entrypoint
```

## Quick Start

1. Create a virtual environment.
2. Install dependencies from `pyproject.toml`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

3. Start by editing the source manifests in `configs/data_sources.json`.
4. Add note/output evaluation samples in `data/eval/gold_examples.jsonl`.
5. Build a normalized corpus manifest from raw text files:

```bash
PYTHONPATH=src python3 scripts/build_normalized_corpus.py
```

6. Build a filtered training-ready corpus:

```bash
PYTHONPATH=src python3 scripts/preprocess_corpus.py
```

7. Run the tokenizer benchmark:

```bash
PYTHONPATH=src python3 scripts/benchmark_tokenizer.py
```

8. Generate a synthetic task-tuning dataset from the filtered corpus:

```bash
PYTHONPATH=src python3 scripts/generate_synthetic_dataset.py
```

9. Inspect the pretraining, task-tuning, and evaluation configs:

```bash
PYTHONPATH=src python3 scripts/show_training_configs.py
```

10. Run the stdlib test suite:

```bash
PYTHONPATH=src python3 scripts/run_tests.py
```

11. Run the Streamlit app once dependencies are installed:

```bash
streamlit run app/streamlit_app.py
```

## Streamlit Cloud

This repo is prepared for Streamlit Community Cloud deployment.

Entry point:

- `app/streamlit_app.py`

Deployment files included:

- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

Step-by-step deployment notes:

- [DEPLOY_STREAMLIT_CLOUD.md](/Users/rakeshnagaragattajayanna/Documents/Codex/2026-04-20-training-a-bilingual-german-english-domain/DEPLOY_STREAMLIT_CLOUD.md)

The core ingestion, preprocessing, evaluation, and tokenizer benchmark scripts are designed to stay close to the Python standard library. The main extra runtime dependency is `streamlit` for the interactive UI.

## What Is Already Working

1. Source manifest loading from JSON configs
2. Raw text and markdown ingestion into normalized JSONL
3. Cleaning, basic language detection, quality scoring, and exact deduplication
4. Tokenizer benchmark reporting over a held-out sample file
5. Gold evaluation scoring for schema and citation checks
6. Synthetic task-data generation for note-to-structure supervision
7. Reusable pretraining, task-tuning, and evaluation config loaders

## Remaining Real-World Work

1. Replace sample raw data with real licensed corpora
2. Install UI/runtime packages such as `streamlit`
3. Add actual tokenizer training with SentencePiece or HF tokenizers
4. Add a real training loop for pretraining and task tuning
5. Swap the heuristic generation backend for a trained checkpoint

## First Implementation Priorities

1. Fill in source ingestion for licensed DE/EN corpora.
2. Implement cleaning and deduplication heuristics.
3. Add tokenizer training and benchmarking.
4. Build the gold evaluation set and validators.
5. Connect the demo app to a real model backend.
