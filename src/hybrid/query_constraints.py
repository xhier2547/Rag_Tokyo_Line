"""Deterministic structured constraint extraction for travel queries."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class QueryConstraints:
    free_only: bool = False
    duration_hours: Optional[float] = None
    max_walk_minutes: Optional[int] = None
    companions: Optional[str] = None
    interests: List[str] = field(default_factory=list)


def extract_query_constraints(query: str) -> QueryConstraints:
    clean = query.lower()
    free_only = any(term in clean for term in ("ฟรี", "ไม่เสียค่า", "ไม่เสียเงิน", "free"))

    duration_hours = None
    duration_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|ชม\.|hours?)", clean)
    if duration_match:
        duration_hours = float(duration_match.group(1))
    elif "ครึ่งวัน" in clean or "half day" in clean:
        duration_hours = 4.0
    elif "หนึ่งวัน" in clean or "1 วัน" in clean or "one day" in clean:
        duration_hours = 8.0

    max_walk_minutes = None
    walk_match = re.search(r"(?:เดิน|ระยะเดิน)[^\d]{0,40}(\d+)\s*นาที", clean)
    if walk_match:
        max_walk_minutes = int(walk_match.group(1))

    companions = None
    companion_groups = {
        "family": ("ครอบครัว", "เด็ก", "family"),
        "solo": ("คนเดียว", "เที่ยวเดี่ยว", "solo"),
        "couple": ("คู่รัก", "แฟน", "couple"),
        "senior": ("ผู้สูงอายุ", "ผู้ใหญ่", "senior"),
    }
    for label, aliases in companion_groups.items():
        if any(alias in clean for alias in aliases):
            companions = label
            break

    interest_groups = {
        "culture": ("วัด", "ศาลเจ้า", "ประวัติ", "วัฒนธรรม"),
        "food": ("อาหาร", "ของกิน", "ตลาด", "สตรีทฟู้ด"),
        "nature": ("สวน", "ธรรมชาติ", "ซากุระ"),
        "anime": ("อนิเมะ", "anime", "เกม", "โปเกมอน"),
        "shopping": ("ช้อป", "shopping", "แฟชั่น"),
        "viewpoint": ("ชมวิว", "วิว", "หอคอย", "กลางคืน"),
    }
    interests = [
        label for label, aliases in interest_groups.items()
        if any(alias in clean for alias in aliases)
    ]

    return QueryConstraints(
        free_only=free_only,
        duration_hours=duration_hours,
        max_walk_minutes=max_walk_minutes,
        companions=companions,
        interests=interests,
    )

