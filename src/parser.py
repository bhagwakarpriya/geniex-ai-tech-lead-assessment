"""Response parsing for structured triage output."""

import re

DEFAULT_VALUES = {
    "category": "other",
    "priority": "medium",
    "assigned_team": "L1",
    "confidence": "LOW",
    "summary": "Unable to parse model response",
}


def parse_triage_response(raw_text):
    """Parse the model's structured response into a dict.

    Extracts FIELD: value pairs from the model's text output.
    Falls back to defaults for any missing field.
    """
    result = {}

    for field in ["CATEGORY", "PRIORITY", "ASSIGNED_TEAM", "CONFIDENCE", "SUMMARY"]:
        match = re.search(rf"{field}:\s*(.+)", raw_text, re.IGNORECASE)
        if match:
            result[field.lower()] = match.group(1).strip()
        else:
            result[field.lower()] = DEFAULT_VALUES[field.lower()]

    return result
