from __future__ import annotations

from bilingual_productivity_llm.common.schemas import TaskType


TASK_SCHEMAS: dict[TaskType, list[str]] = {
    "meeting_minutes": [
        "Title",
        "Date and Time",
        "Participants",
        "Agenda",
        "Discussion Summary",
        "Decisions",
        "Action Items",
        "Open Questions",
        "References",
    ],
    "project_report": [
        "Overview",
        "Progress",
        "Blockers",
        "Risks",
        "Next Steps",
        "References",
    ],
    "study_notes": [
        "Topic",
        "Key Concepts",
        "Definitions",
        "Examples",
        "Summary",
        "References",
    ],
    "professional_summary": [
        "Context",
        "Main Points",
        "Conclusions",
        "Recommended Actions",
        "References",
    ],
}

