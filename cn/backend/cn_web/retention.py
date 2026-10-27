"""Non-destructive retention planning. No deletion is implemented in Phase 1."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal


@dataclass(frozen=True)
class RetentionItem:
    item_id: str
    category: Literal["temporary_preview", "cache", "abandoned_upload", "source_statement", "calculation", "scheme", "issued_cn", "backup"]
    created_at: datetime
    last_used_at: datetime
    linked_to_saved_work: bool = False
    active: bool = False


def cleanup_candidates(items, *, now: datetime, age_days=60):
    """Draft interpretation of two months: 60 days, adjustable by admin later.

    Saved sources, history and backups are never selected by inactivity alone.
    Both creation and last-use dates must be older than the cutoff.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("A timezone-aware current time is required")
    if type(age_days) is not int or age_days < 1:
        raise ValueError("Retention age must be a positive integer")
    cutoff = now - timedelta(days=age_days)
    result = []
    for item in items:
        if any(t.tzinfo is None or t.utcoffset() is None for t in (item.created_at, item.last_used_at)):
            raise ValueError("Retention timestamps must be timezone-aware")
        if (item.category in {"temporary_preview", "cache", "abandoned_upload"}
                and not item.linked_to_saved_work and not item.active
                and max(item.created_at, item.last_used_at) < cutoff):
            result.append(item.item_id)
    return result
