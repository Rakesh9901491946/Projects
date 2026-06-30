# Technical Architecture: Bilingual DE/EN Domain LLM for Structured Productivity Writing

## 1. Project Goal

Build a small bilingual German-English language model from scratch that converts messy notes into clean, structured outputs for academic and workplace use. The system should support tasks such as:

- meeting minutes
- project reports
- study notes
- professional summaries
- citation-aware outputs with bibliography formatting

The project is intentionally end-to-end. It includes open-licensed data collection, tokenizer training, pretraining, supervised task tuning, evaluation, and a Streamlit demo.

The core success criterion is not conversational quality. It is reliable transformation of incomplete or noisy notes into structured, faithful, bilingual outputs.

## 2. Product Requirements

### Primary use cases

- Students turning lecture notes into study summaries
- Students and staff converting meeting notes into minutes
- Teams producing short project reports from bullet notes
- Users generating concise professional summaries from rough notes
- Users receiving consistently formatted citations and bibliography sections

### Functional requirements

- Accept German, English, and mixed-language notes
- Generate outputs in a requested template
- Preserve facts from notes without adding unsupported details
- Produce consistent headings, sections, bullets, and formatting
- Support citation and bibliography formatting rules
- Run through a simple demo app for interactive testing

### Non-functional requirements

- Training data must be open-licensed or clearly reusable
- Data lineage must be reproducible and auditable
- Evaluation must include factual consistency and formatting validity
- The first system should prioritize correctness over model size
- Every stage should be rerunnable with versioned configs

## 3. System Strategy

Treat the project as two connected layers:

1. Base bilingual language modeling
2. Structured transformation of notes into output schemas

The base model should learn DE/EN grammar, terminology, syntax, and document style from general and domain-specific corpora. A second stage should specialize the model for note-to-structure tasks using curated and synthetic supervision.

This separation keeps training objectives clean:

- pretraining teaches language and domain coverage
- task tuning teaches template obedience, transformation behavior, and citation formatting

## 4. Target Outputs

The model should generate a small set of strongly defined output formats rather than an unconstrained range of documents.

### Output family A: Meeting minutes

Required sections:

- title
- date and time
- participants
- agenda
- discussion summary
- decisions
- action items
- open questions

### Output family B: Project report

Required sections:

- overview
- progress
- blockers
- risks
- next steps
- references

### Output family C: Study notes

Required sections:

- topic
- key concepts
- definitions
- examples
- summary
- references

### Output family D: Professional summary

Required sections:

- context
- main points
- conclusions
- recommended actions
- references

The schemas should be versioned and machine-checkable so the evaluator can score structural compliance.

## 5. Data Architecture

The dataset should be split into four layers with immutable artifacts.

### Layer 0: Raw source snapshots

Store original source files plus metadata:

- source URL
- license
- acquisition date
- language label
- document type
- checksum

Candidate sources:

- German and English Wikipedia dumps
- EU documents
- German and EU public sector reports
- OER repositories
- public parliamentary or administrative publications with clear licenses
- public educational resources
- openly licensed domain glossaries

Avoid sources with uncertain licensing or weak provenance.

### Layer 1: Normalized text corpus

Transform raw files into a common document format:

```json
{
  "doc_id": "stable-id",
  "source": "wikipedia_de",
  "license": "CC-BY-SA",
  "language": "de",
  "title": "Document title",
  "text": "normalized text",
  "sections": [],
  "metadata": {}
}
```

Normalization tasks:

- extract text from XML, HTML, PDF, DOCX, and plain text
- normalize Unicode and whitespace
- remove boilerplate navigation and repeated headers
- preserve basic structural boundaries like headings and lists
- attach provenance fields

### Layer 2: Deduplicated and quality-filtered corpus

Apply:

- exact deduplication by checksum
- near-duplicate detection with MinHash or LSH
- language identification
- document length filtering
- OCR-noise filtering
- quality heuristics for malformed or low-information documents

Store quality flags, not just binary decisions. This helps debug why useful documents were discarded.

### Layer 3: Training-ready shards

Export tokenization-ready shards split by:

- language: `de`, `en`, `mixed`
- domain: `encyclopedic`, `government`, `education`, `workplace`, `reference`
- training stage: `pretrain`, `task_tune`, `eval`

Each shard should be versioned and accompanied by a manifest.

## 6. Data Collection Plan

### 6.1 General bilingual pretraining data

Purpose:

- build broad DE/EN language competence
- stabilize syntax and fluency
- cover general knowledge and document structures

Sources:

- Wikipedia DE and EN
- Wikibooks or other open educational sources where licensing is clear
- EU legislation, reports, and summaries with reusable terms
- public administrative documents
- open course materials

### 6.2 Domain-specific data

Purpose:

- expose the model to formal summary and report style
- teach terminology relevant to productivity and education

Target content:

- meeting agendas and public minutes where reusable
- educational handouts
- study materials
- project documentation templates
- report-style public documents

### 6.3 Task-tuning data

Purpose:

- teach note-to-template transformation
- teach structured writing discipline
- teach citations and bibliography patterns

Sources:

- hand-authored examples
- synthetic note/output pairs generated from open documents
- lightly templated transformations of public documents
- bilingual paraphrase and translation pairs when license permits

This dataset should not be a random instruction dataset. It should be highly targeted to your task family.

## 7. Data Cleaning and Filtering

### 7.1 Core cleaning rules

- strip repeated headers and footers
- collapse excessive whitespace
- preserve bullets and section boundaries
- normalize quotation marks and punctuation where safe
- retain citations, references, dates, lists, and names

### 7.2 Language handling

Run document-level and chunk-level language identification.

Store:

- primary language
- secondary language if mixed
- confidence score

This matters because bilingual note inputs may switch language mid-document.

### 7.3 Deduplication

Use a two-pass strategy:

1. exact deduplication on normalized text
2. fuzzy deduplication with MinHash similarity

Keep one canonical copy and record duplicate clusters so analysis remains possible.

### 7.4 Quality scoring

Assign a quality score per document using features such as:

- alphabetic character ratio
- repeated line ratio
- malformed token ratio
- language confidence
- stopword plausibility
- OCR corruption signals
- boilerplate percentage

Do not trust a single threshold. Keep the score and filtering reason in metadata.

## 8. Note-Oriented Augmentation

One of the biggest risks is mismatch between polished source documents and messy real notes. To reduce that gap, create a note simulation pipeline.

Transform clean source text into noisy note-like variants by applying controlled corruption:

- shorten sentences into fragments
- drop function words
- convert paragraphs into bullets
- add timestamps or shorthand markers
- mix German and English terms
- introduce repetition
- remove explicit connectives
- keep source facts intact

This creates paired data:

- source paragraph or structured source document
- noisy notes derived from source
- target structured output

The augmentation should imitate realistic student and workplace note patterns without inventing facts.

## 9. Tokenizer Design

Train a single shared tokenizer for DE and EN.

### Why a shared tokenizer

- supports mixed-language inputs
- avoids language-switch friction
- simplifies deployment
- encourages parameter sharing for shared vocabulary and structure

### Tokenizer requirements

- good compression on German compounds
- stable treatment of English technical terms
- efficient handling of bullets, headings, dates, references, and citation markers
- acceptable segmentation for names, abbreviations, and URLs

### Recommended approach

- SentencePiece Unigram or BPE
- vocabulary size in the range of 32k to 50k for a small model
- evaluate multiple candidate vocabularies instead of choosing by habit

### Tokenizer evaluation set

Create a held-out tokenizer benchmark with:

- German compounds
- English domain terminology
- mixed DE/EN notes
- bullet-heavy note fragments
- citation strings
- bibliography lines
- names, acronyms, and dates

Track:

- average chars per token
- fragmentation of key terms
- fragmentation of citations and URLs
- language-specific token efficiency

## 10. Model Architecture

### Recommended first model

Start with a decoder-only transformer in the small range, for example:

- 100M to 350M parameters for the first serious run

This size is large enough to demonstrate meaningful behavior while still allowing multiple end-to-end experiments.

### Why not start bigger

- data recipe errors are more expensive at larger scale
- training bugs become costly
- evaluation and iteration slow down
- a smaller model is sufficient to validate bilingual structure generation

### Baseline architecture

- decoder-only transformer
- rotary positional embeddings
- RMSNorm
- SwiGLU or GELU MLP
- grouped-query attention if supported by your stack

The architecture should be simple and stable rather than novel.

## 11. Pretraining Recipe

### Objective

Standard causal language modeling over the cleaned bilingual corpus.

### Sampling strategy

Use weighted sampling to avoid English overwhelming German. A starting point:

- German: 40 to 50 percent
- English: 40 to 50 percent
- mixed or synthetic bilingual: 5 to 15 percent

Tune the ratio after tokenizer and early validation results.

### Sequence strategy

- train with packed sequences for efficiency
- preserve some document boundaries
- include lists, headings, and structured text intact

### Curriculum

Optional but useful:

1. train on high-quality general and domain text
2. introduce more note-like and mixed-language shards later

This can stabilize early learning.

### Artifacts to save

- tokenizer files
- training config
- data manifest
- checkpoints by step
- validation metrics
- random seed and environment details

## 12. Task Tuning

Task tuning should specialize the base model for constrained productivity outputs.

### Task format

Each example should define:

- task type
- input notes
- target language
- output schema
- desired citation style
- expected output

Example logical format:

```json
{
  "task": "meeting_minutes",
  "language": "de",
  "citation_style": "apa-like",
  "notes": "... messy notes ...",
  "target": "... structured minutes ..."
}
```

### Data creation strategy

Combine:

- manually curated gold examples
- synthetic examples from public documents
- bilingual translation-aligned task examples
- adversarial messy-note examples

### Important constraint

The target output must be faithful to the notes. If the source notes do not mention a fact, the target must not include it.

This fidelity rule should be explicit during data creation.

## 13. Citation and Bibliography Handling

This is a fragile area for pure generation. Use a hybrid strategy.

### Model responsibilities

- recognize when a citation or reference section is required
- place citation markers consistently
- produce bibliographic entries in the requested style skeleton

### Rule-based or validator responsibilities

- enforce formatting consistency
- check required fields
- normalize punctuation
- reject incomplete or suspicious bibliography items

This reduces hallucinated references and inconsistent formatting. In practice, the model should draft references from provided note metadata or source metadata, while a deterministic formatter validates and normalizes them.

## 14. Evaluation Framework

Evaluation must be centered on user tasks, not only on language-model metrics.

### 14.1 Pretraining evaluation

Track:

- validation loss
- perplexity by language
- perplexity by domain shard
- tokenizer efficiency diagnostics

### 14.2 Task evaluation

Use a held-out benchmark of note-to-output examples across DE, EN, and mixed inputs.

Score the following:

- factual consistency with notes
- structural validity against the target schema
- bilingual fluency and grammatical quality
- coverage of important points from the notes
- citation and bibliography consistency
- robustness under noisy input

### 14.3 Factual consistency scoring

Use a combination of:

- exact span support checks for names, dates, and numbers
- entailment or QA-based factual verification
- manual review on a smaller gold set

Critical factual errors include:

- invented participants
- invented dates
- unsupported claims
- fabricated references

### 14.4 Format validation

For each output family, define validators:

- required section presence
- valid section ordering
- non-empty required fields
- valid action-item format where needed
- valid bibliography pattern

This should be a hard metric, not just a subjective review criterion.

### 14.5 Bilingual quality evaluation

Measure:

- language correctness
- unintended language switching
- preservation of mixed-language terminology where appropriate
- translation consistency when target language differs from note language

Include human review because automatic bilingual quality metrics can miss register and terminology issues.

## 15. Gold Evaluation Set Design

Build a small, carefully curated benchmark before large-scale training.

Recommended composition:

- 100 to 300 examples for initial development
- balanced across meeting minutes, reports, study notes, and summaries
- balanced across German, English, and mixed notes
- varied note quality from clean bullets to highly messy fragments

Each example should contain:

- raw notes
- reference structured output
- language label
- task label
- citation expectation
- key facts list for factual checking

This set becomes the anchor for model comparison across all experiments.

## 16. Training Stack

Use a simple, reproducible stack with strong community support.

### Suggested tooling

- data processing: Python, Polars or pandas, datasets, BeautifulSoup, lxml, PDF extraction tools
- deduplication: datasketch or custom MinHash pipeline
- tokenizer: SentencePiece or Hugging Face tokenizers
- training: PyTorch with Transformers or a lightweight custom training loop
- experiment tracking: Weights & Biases or MLflow
- config management: YAML or Hydra
- artifact storage: versioned local or cloud storage

### Repository structure

```text
project/
  configs/
  data/
    manifests/
    eval/
  src/
    ingest/
    clean/
    dedup/
    filter/
    tokenize/
    pretrain/
    tune/
    eval/
    demo/
  scripts/
  outputs/
  app/
```

## 17. Pipeline Stages

### Stage A: Source ingestion

Input:

- raw dumps and documents

Output:

- normalized documents with metadata

### Stage B: Corpus cleaning

Input:

- normalized documents

Output:

- cleaned text corpus with quality metadata

### Stage C: Deduplication and filtering

Input:

- cleaned corpus

Output:

- final pretraining corpus

### Stage D: Tokenizer training

Input:

- sampled bilingual corpus

Output:

- tokenizer model and tokenizer evaluation report

### Stage E: Base pretraining

Input:

- tokenizer
- pretraining shards

Output:

- bilingual base model checkpoints

### Stage F: Task tuning

Input:

- base checkpoint
- note-to-structure task dataset

Output:

- task-specialized model

### Stage G: Evaluation

Input:

- tuned model
- held-out benchmark

Output:

- metric report
- error analysis report

### Stage H: Demo deployment

Input:

- tuned model
- validators

Output:

- Streamlit prototype

## 18. Streamlit Demo Architecture

The demo should make the model inspectable, not just attractive.

### User workflow

1. User pastes notes
2. User selects task type
3. User selects output language
4. User selects citation style
5. System generates output
6. Validator checks structure and references
7. UI shows output plus warnings

### Recommended interface panels

- input notes
- generation settings
- generated output
- extracted entities and dates
- validation results
- citation and bibliography check
- debug metadata such as detected language and model version

### Safety behaviors

- flag unsupported citations
- warn on likely hallucinated details
- show detected missing sections
- allow regeneration with stricter structure controls

## 19. Risk Register

### Risk 1: Clean-text bias

Issue:

- pretraining data is cleaner than real note input

Mitigation:

- note simulation augmentation
- real note collection if licensing and privacy permit
- noisy evaluation benchmark

### Risk 2: German underperformance

Issue:

- English may dominate corpus and tokenizer behavior

Mitigation:

- controlled sampling ratios
- language-specific validation
- German-focused tokenizer benchmark

### Risk 3: Hallucinated references

Issue:

- model invents bibliography content

Mitigation:

- hybrid citation pipeline
- metadata-grounded task data
- bibliography validator

### Risk 4: Poor schema compliance

Issue:

- outputs omit sections or drift from template

Mitigation:

- schema-specific task tuning
- hard format validators
- training examples with strict template consistency

### Risk 5: Misleading evaluation

Issue:

- strong generic language scores hide weak task faithfulness

Mitigation:

- prioritize factual and structural metrics
- use human review on a gold benchmark

## 20. Milestone Plan

### Milestone 1: Data foundation

Deliverables:

- source inventory with licenses
- normalization pipeline
- cleaned and deduplicated pilot corpus

Exit criteria:

- reproducible manifests
- quality filtering report

### Milestone 2: Tokenizer

Deliverables:

- tokenizer candidates
- tokenizer benchmark report

Exit criteria:

- chosen tokenizer performs acceptably on DE, EN, and mixed notes

### Milestone 3: Base model

Deliverables:

- first pretrained checkpoint
- per-language validation curves

Exit criteria:

- stable training
- no obvious language collapse

### Milestone 4: Task tuning

Deliverables:

- task dataset
- tuned checkpoint

Exit criteria:

- measurable improvement on schema compliance and faithfulness

### Milestone 5: Evaluation suite

Deliverables:

- validators
- benchmark runner
- error analysis notebook or report

Exit criteria:

- repeatable comparison across checkpoints

### Milestone 6: Demo app

Deliverables:

- Streamlit interface
- model and validator integration

Exit criteria:

- users can test DE, EN, and mixed notes end to end

## 21. Recommended First Iteration Scope

To keep the project tractable, the first full cycle should be narrower than the full vision.

Recommended initial scope:

- tasks: meeting minutes and study notes only
- languages: German and English, plus a small mixed subset
- model size: small baseline
- citations: one clearly defined style
- demo: text input plus validation panel

This reduces surface area while preserving the core research value.

## 22. Suggested Immediate Next Actions

1. Define the exact license-approved source list and collection method.
2. Build the document normalization schema and manifests.
3. Assemble a pilot corpus and inspect failure cases manually.
4. Create a tokenizer benchmark set before training the tokenizer.
5. Build a small gold note-to-output benchmark with strict schemas.
6. Train a first small base model before scaling data or parameters.
7. Add task tuning only after base bilingual behavior is stable.

## 23. Key Design Principles

- Favor reproducibility over speed hacks in early stages.
- Keep every dataset stage versioned and inspectable.
- Optimize for factual faithfulness, not chat style.
- Use validators wherever formatting can be checked deterministically.
- Keep bilingual balance explicit at every stage.
- Start small enough to iterate and large enough to learn something real.

## 24. Final Recommendation

The most effective path is to build this as a structured generation system on top of a small bilingual base model, not as a generic assistant. If the dataset, schemas, validators, and faithfulness benchmark are designed carefully, even a relatively small model can become genuinely useful for note-to-document productivity tasks.

The project will succeed or fail more on data design and evaluation discipline than on model novelty. The cleanest next implementation artifact after this architecture is a repository scaffold with:

- dataset manifests
- schema definitions
- tokenizer benchmark samples
- task dataset format
- evaluation validators

That scaffold should be the next build step.
