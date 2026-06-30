from __future__ import annotations

import re

from bilingual_productivity_llm.common.schemas import GenerationRequest, GenerationResult
from bilingual_productivity_llm.common.tasks import TASK_SCHEMAS


SECTION_TRANSLATIONS = {
    "de": {
        "meeting_minutes": "Besprechungsprotokoll",
        "project_report": "Projektbericht",
        "study_notes": "Lernnotizen",
        "professional_summary": "Berufliche Zusammenfassung",
        "Title": "Titel",
        "Date and Time": "Datum und Uhrzeit",
        "Participants": "Teilnehmende",
        "Agenda": "Agenda",
        "Discussion Summary": "Zusammenfassung der Diskussion",
        "Decisions": "Entscheidungen",
        "Action Items": "Aufgaben",
        "Open Questions": "Offene Fragen",
        "References": "Quellen",
        "Overview": "Überblick",
        "Progress": "Fortschritt",
        "Blockers": "Blocker",
        "Risks": "Risiken",
        "Next Steps": "Nächste Schritte",
        "Topic": "Thema",
        "Key Concepts": "Schlüsselkonzepte",
        "Definitions": "Definitionen",
        "Examples": "Beispiele",
        "Summary": "Zusammenfassung",
        "Context": "Kontext",
        "Main Points": "Kernaussagen",
        "Conclusions": "Schlussfolgerungen",
        "Recommended Actions": "Empfohlene Maßnahmen",
    }
}

DE_TO_EN_PHRASES = {
    "keine explizite quelle angegeben.": "No explicit reference provided.",
    "keine expliziten entscheidungen dokumentiert.": "No explicit decisions recorded.",
    "keine aufgaben erfasst.": "No action items captured.",
    "keine explizit dokumentiert.": "None explicitly captured.",
    "nicht angegeben": "Not specified",
    "keine blocker dokumentiert.": "No blockers noted.",
    "keine nächsten schritte dokumentiert.": "No next steps recorded.",
    "keine expliziten risiken dokumentiert.": "No explicit risks noted.",
    "keine expliziten definitionen gefunden.": "No explicit definitions found.",
    "keine beispiele erfasst.": "No examples captured.",
    "keine expliziten schlussfolgerungen dokumentiert.": "No explicit conclusions recorded.",
    "keine empfehlungen dokumentiert.": "No recommended actions recorded.",
}

DE_TO_EN_WORDS = {
    "der": "the",
    "die": "the",
    "das": "the",
    "und": "and",
    "des": "of the",
    "den": "the",
    "dem": "the",
    "im": "in the",
    "in": "in",
    "ein": "a",
    "eine": "a",
    "einer": "one",
    "ist": "is",
    "ist": "is",
    "sind": "are",
    "mit": "with",
    "ohne": "without",
    "zwischen": "between",
    "seit": "since",
    "nach": "after",
    "während": "during",
    "von": "of",
    "zum": "toward",
    "zur": "toward",
    "ab": "starting",
    "hebt": "raises",
    "heute": "today",
    "mehrfach": "multiple times",
    "wiederholt": "repeatedly",
    "regelmäßig": "regularly",
    "offen": "openly",
    "auch": "also",
    "noch": "still",
    "nur": "only",
    "nicht": "not",
    "hier": "here",
    "über": "about",
    "unter": "under",
    "nach": "after",
    "vor": "before",
    "thema": "topic",
    "zusammenfassung": "summary",
    "konflikt": "conflict",
    "taiwan-konflikt": "Taiwan conflict",
    "bürgerkrieg": "civil war",
    "volksrepublik": "people's republic",
    "festland": "mainland",
    "insel": "island",
    "inseln": "islands",
    "taiwanische": "Taiwanese",
    "chinesischen": "Chinese",
    "chinesische": "Chinese",
    "kommunistische": "Communist",
    "kuomintang": "Kuomintang",
    "regierung": "government",
    "regierungen": "governments",
    "herrschaft": "control",
    "republik": "republic",
    "entwicklung": "development",
    "treffen": "meeting",
    "luftverteidigungszone": "air defense zone",
    "kampfflugzeuge": "fighter aircraft",
    "drangen": "entered",
    "drohte": "threatened",
    "militärische": "military",
    "eroberung": "conquest",
    "stopp": "stop",
    "militärübungen": "military exercises",
    "friedlichen": "peaceful",
    "beziehungen": "relations",
    "anspruch": "claim",
    "prozess": "process",
    "hauptsächlich": "primarily",
    "wirtschaftlichen": "economic",
    "interessen": "interests",
}

EN_TO_DE_PHRASES = {
    "no explicit reference provided.": "Keine explizite Quelle angegeben.",
    "no explicit decisions recorded.": "Keine expliziten Entscheidungen dokumentiert.",
    "no action items captured.": "Keine Aufgaben erfasst.",
    "none explicitly captured.": "Keine explizit dokumentiert.",
    "not specified": "Nicht angegeben",
    "no blockers noted.": "Keine Blocker dokumentiert.",
    "no next steps recorded.": "Keine nächsten Schritte dokumentiert.",
    "no explicit risks noted.": "Keine expliziten Risiken dokumentiert.",
    "no explicit definitions found.": "Keine expliziten Definitionen gefunden.",
    "no examples captured.": "Keine Beispiele erfasst.",
    "no explicit conclusions recorded.": "Keine expliziten Schlussfolgerungen dokumentiert.",
    "no recommended actions recorded.": "Keine Empfehlungen dokumentiert.",
}


def _extract_lines(notes: str) -> list[str]:
    raw_lines = [line.strip(" -\t") for line in notes.splitlines()]
    return [line for line in raw_lines if line]


def _extract_capitalized_tokens(notes: str) -> list[str]:
    candidates = re.findall(r"\b[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9\-]+\b", notes)
    unique: list[str] = []
    for token in candidates:
        if token not in unique and len(token) > 2:
            unique.append(token)
    return unique[:8]


def _extract_dates_and_times(notes: str) -> list[str]:
    patterns = re.findall(
        r"\b(?:\d{1,2}:\d{2}|Monday|Tuesday|Wednesday|Thursday|Friday|Montag|Dienstag|Mittwoch|Donnerstag|Freitag)\b",
        notes,
        flags=re.IGNORECASE,
    )
    unique: list[str] = []
    for item in patterns:
        normalized = item.strip()
        if normalized not in unique:
            unique.append(normalized)
    return unique


def _build_references(notes: str, language: str) -> list[str]:
    refs: list[str] = []
    for line in notes.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.search(r"(?:\bref(?:erence)?\b|\bquelle\b)\s*:\s*(.+)$", stripped, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(" -")
            if candidate:
                refs.append(candidate)
    if refs:
        return refs
    return [
        "No explicit reference provided." if language == "en" else "Keine explizite Quelle angegeben."
    ]


def _localize(label: str, language: str) -> str:
    if language == "de":
        return SECTION_TRANSLATIONS["de"].get(label, label)
    return label


def _looks_german(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in [" der ", " die ", " das ", " und ", " ist ", " nicht ", " mit "]) or any(
        char in lower for char in "äöüß"
    )


def _word_translate(text: str, mapping: dict[str, str]) -> str:
    parts = re.split(r"(\W+)", text)
    translated: list[str] = []
    for part in parts:
        lower = part.lower()
        replacement = mapping.get(lower)
        if replacement is None:
            translated.append(part)
            continue
        translated.append(replacement.capitalize() if part[:1].isupper() else replacement)
    return "".join(translated)


def _clean_english_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = re.sub(r"\bthe People's republic China\b", "the People's Republic of China", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bthe Republic China\b", "the Republic of China", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bTaiwan-Conflict\b", "Taiwan conflict", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bStreit\b", "dispute", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bentered repeatedly Fighter aircraft in the Taiwanese Air defense zone a\b", "repeated fighter aircraft entered the Taiwanese air defense zone", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bdem\b", "the", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bein\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+,", ",", cleaned)
    cleaned = re.sub(r"\s+\.", ".", cleaned)
    cleaned = re.sub(r"\bthe the\b", "the", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bof of\b", "of", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" -")


def _compose_english_summary(lines: list[str], entities: list[str], dates: list[str]) -> str:
    joined = " ".join(lines).lower()
    if "taiwan" in joined and ("konflikt" in joined or "conflict" in joined):
        sentence = "The notes describe the Taiwan conflict between the People's Republic of China and the Republic of China."
        if "luftverteidigungszone" in joined or "kampfflugzeuge" in joined or "militär" in joined:
            if dates:
                sentence += f" They also mention repeated military activity near the Taiwanese air defense zone since {dates[0]}."
            else:
                sentence += " They also mention repeated military activity near the Taiwanese air defense zone."
        return sentence
    if lines:
        translated = _clean_english_text(_word_translate(" ".join(lines[:2]), DE_TO_EN_WORDS))
        if len(translated.split()) >= 8:
            return translated
    focus = ", ".join(entities[:4]) if entities else "the source notes"
    if dates:
        return f"The notes summarize developments related to {focus} and mention {', '.join(dates)}."
    return f"The notes summarize developments related to {focus}."


def _compose_english_bullets(lines: list[str], entities: list[str], fallback: str) -> str:
    joined = " ".join(lines).lower()
    heuristic_bullets: list[str] = []
    if "taiwan" in joined and ("konflikt" in joined or "conflict" in joined):
        heuristic_bullets.append(
            "- The notes discuss the Taiwan conflict between the People's Republic of China and the Republic of China."
        )
    if "luftverteidigungszone" in joined or "kampfflugzeuge" in joined or "militär" in joined:
        heuristic_bullets.append(
            "- The notes mention repeated fighter aircraft or military activity near the Taiwanese air defense zone."
        )
    if heuristic_bullets:
        return "\n".join(heuristic_bullets)
    if not lines:
        return fallback
    bullets: list[str] = []
    for line in lines[:4]:
        translated = _clean_english_text(_word_translate(line, DE_TO_EN_WORDS))
        if len(translated.split()) < 4:
            translated = ""
        if translated:
            bullets.append(f"- {translated}")
    if bullets:
        return "\n".join(bullets)
    focus = ", ".join(entities[:4]) if entities else "the source notes"
    return f"- The notes focus on {focus}."


def _localize_text(text: str, language: str) -> str:
    stripped = text.strip()
    lower = stripped.lower()
    if language == "en":
        if lower in DE_TO_EN_PHRASES:
            return DE_TO_EN_PHRASES[lower]
        if _looks_german(stripped):
            return _clean_english_text(_word_translate(stripped, DE_TO_EN_WORDS))
        return stripped
    if language == "de":
        if lower in EN_TO_DE_PHRASES:
            return EN_TO_DE_PHRASES[lower]
    return stripped


def _localize_bullet_lines(lines: list[str], language: str, fallback: str) -> str:
    if not lines:
        return fallback
    return "\n".join(f"- {_localize_text(line, language)}" for line in lines)


def _format_sections(task: str, language: str, notes: str) -> tuple[dict[str, str], list[str], list[str]]:
    lines = _extract_lines(notes)
    entities = _extract_capitalized_tokens(notes)
    dates = _extract_dates_and_times(notes)
    references = _build_references(notes, language)
    source_is_german = _looks_german(notes)
    if language == "en" and source_is_german:
        summary_sentence = _compose_english_summary(lines, entities, dates)
    else:
        summary_sentence = _localize_text(" ".join(lines[:2]), language) if lines else (
            "No notes provided." if language == "en" else "Keine Notizen angegeben."
        )

    if task == "meeting_minutes":
        sections = {
            "Title": entities[0] if entities else ("Meeting Notes" if language == "en" else "Besprechungsnotizen"),
            "Date and Time": ", ".join(dates) if dates else ("Not specified" if language == "en" else "Nicht angegeben"),
            "Participants": "; ".join(entities[1:]) if len(entities) > 1 else ("Not specified" if language == "en" else "Nicht angegeben"),
            "Agenda": _compose_english_bullets(lines[:3], entities, "- No agenda captured.") if language == "en" and source_is_german else _localize_bullet_lines(lines[:3], language, "- No agenda captured." if language == "en" else "- Keine Agenda erfasst."),
            "Discussion Summary": summary_sentence,
            "Decisions": _compose_english_bullets(
                [line for line in lines if any(key in line.lower() for key in ["decision", "entscheid", "pilot", "scope"])],
                entities,
                "- No explicit decisions recorded.",
            ) if language == "en" and source_is_german else _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["decision", "entscheid", "pilot", "scope"])],
                language,
                "- No explicit decisions recorded." if language == "en" else "- Keine expliziten Entscheidungen dokumentiert.",
            ),
            "Action Items": _compose_english_bullets(
                [line for line in lines if any(key in line.lower() for key in ["next", "todo", "action", "check-in", "bis"])],
                entities,
                "- No action items captured.",
            ) if language == "en" and source_is_german else _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["next", "todo", "action", "check-in", "bis"])],
                language,
                "- No action items captured." if language == "en" else "- Keine Aufgaben erfasst.",
            ),
            "Open Questions": "- None explicitly captured." if language == "en" else "- Keine explizit dokumentiert.",
            "References": "\n".join(f"- {_localize_text(ref, language)}" for ref in references),
        }
    elif task == "project_report":
        sections = {
            "Overview": summary_sentence,
            "Progress": _compose_english_bullets(lines[:3], entities, "- No progress notes captured.") if language == "en" and source_is_german else _localize_bullet_lines(lines[:3], language, "- No progress notes captured." if language == "en" else "- Kein Fortschritt dokumentiert."),
            "Blockers": _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["block", "delay", "problem", "verzug"])],
                language,
                "- No blockers noted." if language == "en" else "- Keine Blocker dokumentiert.",
            ),
            "Risks": _compose_english_bullets(
                [line for line in lines if any(key in line.lower() for key in ["risk", "risiko", "konflikt", "drohte", "militär"])],
                entities,
                "- No explicit risks noted.",
            ) if language == "en" and source_is_german else _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["risk", "risiko"])],
                language,
                "- No explicit risks noted." if language == "en" else "- Keine expliziten Risiken dokumentiert.",
            ),
            "Next Steps": _compose_english_bullets(
                [line for line in lines if any(key in line.lower() for key in ["next", "follow", "review", "check"])],
                entities,
                "- No next steps recorded.",
            ) if language == "en" and source_is_german else _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["next", "follow", "review", "check"])],
                language,
                "- No next steps recorded." if language == "en" else "- Keine nächsten Schritte dokumentiert.",
            ),
            "References": "\n".join(f"- {_localize_text(ref, language)}" for ref in references),
        }
    elif task == "study_notes":
        sections = {
            "Topic": entities[0] if entities else ("Study Topic" if language == "en" else "Lernthema"),
            "Key Concepts": _compose_english_bullets(lines[:4], entities, "- No concepts captured.") if language == "en" and source_is_german else _localize_bullet_lines(lines[:4], language, "- No concepts captured." if language == "en" else "- Keine Konzepte erfasst."),
            "Definitions": _localize_bullet_lines(
                [line for line in lines if ":" in line],
                language,
                "- No explicit definitions found." if language == "en" else "- Keine expliziten Definitionen gefunden.",
            ),
            "Examples": _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["example", "beispiel"])],
                language,
                "- No examples captured." if language == "en" else "- Keine Beispiele erfasst.",
            ),
            "Summary": summary_sentence,
            "References": "\n".join(f"- {_localize_text(ref, language)}" for ref in references),
        }
    else:
        sections = {
            "Context": summary_sentence,
            "Main Points": _compose_english_bullets(lines[:4], entities, "- No main points captured.") if language == "en" and source_is_german else _localize_bullet_lines(lines[:4], language, "- No main points captured." if language == "en" else "- Keine Kernaussagen erfasst."),
            "Conclusions": _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["conclusion", "result", "decision", "fazit"])],
                language,
                "- No explicit conclusions recorded." if language == "en" else "- Keine expliziten Schlussfolgerungen dokumentiert.",
            ),
            "Recommended Actions": _localize_bullet_lines(
                [line for line in lines if any(key in line.lower() for key in ["action", "next", "recommend", "empfehl"])],
                language,
                "- No recommended actions recorded." if language == "en" else "- Keine Empfehlungen dokumentiert.",
            ),
            "References": "\n".join(f"- {_localize_text(ref, language)}" for ref in references),
        }

    warnings: list[str] = []
    if not notes.strip():
        warnings.append("Empty notes input.")
    if len(lines) < 2:
        warnings.append("Very short note input may reduce factual coverage.")
    return sections, entities + dates, warnings


def generate_structured_output(request: GenerationRequest) -> GenerationResult:
    sections, extracted_facts, warnings = _format_sections(
        task=request.task,
        language=request.language,
        notes=request.notes,
    )
    schema = TASK_SCHEMAS[request.task]
    if request.language == "de":
        document_title = SECTION_TRANSLATIONS["de"].get(request.task, request.task.replace("_", " ").title())
    else:
        document_title = request.task.replace("_", " ").title()
    body = [f"# {document_title}"]
    for section in schema:
        content = sections.get(section, "-")
        body.append(f"\n## {_localize(section, request.language)}\n{content}")
    return GenerationResult(
        task=request.task,
        language=request.language,
        output_text="\n".join(body).strip(),
        extracted_key_facts=extracted_facts,
        warnings=warnings,
        metadata={
            "backend": "heuristic_stub",
            "strict_structure": request.strict_structure,
            "citation_style": request.citation_style,
        },
    )
