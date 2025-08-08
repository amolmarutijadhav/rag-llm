from typing import Any, Dict
from app.core.logging_config import sanitize_for_logging


def log_extra(event_type: str, **fields: Any) -> Dict[str, Dict[str, Any]]:
    """Helper to build structured logging extras consistently.

    Always uses an 'event_type' key inside 'extra_fields'.
    Do not include correlation_id here; it is injected by the formatter.
    """
    return {"extra_fields": {"event_type": event_type, **fields}}


class RedactionFilter:
    """Logging filter that sanitizes extra_fields to prevent PII leaks."""

    def filter(self, record) -> bool:  # type: ignore[override]
        try:
            if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
                record.extra_fields = sanitize_for_logging(record.extra_fields)
        except Exception:
            # Never break logging on redaction failure
            pass
        return True


