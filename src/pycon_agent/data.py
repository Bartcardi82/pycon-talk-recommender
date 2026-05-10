from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Talk:
    title: str
    speaker: str
    abstract: str | None
    track: str | None
    room: str
    date: str
    start: str
    duration: str

    def summary(self) -> str:
        parts = [
            f"**{self.title}**",
            f"Speaker: {self.speaker}",
            f"Track: {self.track or 'N/A'}",
            f"When: {self.date} {self.start} ({self.duration})",
            f"Room: {self.room}",
        ]
        if self.abstract:
            snippet = self.abstract[:200] + ("..." if len(self.abstract) > 200 else "")
            parts.append(f"Abstract: {snippet}")
        return "\n".join(parts)


SKIP_TYPES = {
    "lightning talks", "opening session", "panel", "social event",
    "lunch", "break", "coffee", "registration", "plenary",
}


def load_schedule(path: str | Path) -> list[Talk]:
    raw = json.loads(Path(path).read_text())
    days = raw["schedule"]["conference"]["days"]
    talks: list[Talk] = []

    for day in days:
        date = day["date"]
        for room_name, entries in day["rooms"].items():
            for entry in entries:
                title = entry.get("title", "")
                entry_type = (entry.get("type") or "").lower()

                if entry_type in SKIP_TYPES:
                    continue
                if any(skip in title.lower() for skip in SKIP_TYPES):
                    continue

                persons = entry.get("persons", [])
                speaker = ", ".join(
                    p.get("public_name", "Unknown") for p in persons
                ) if persons else "Unknown"

                talks.append(Talk(
                    title=title,
                    speaker=speaker,
                    abstract=entry.get("abstract"),
                    track=entry.get("track"),
                    room=room_name,
                    date=date,
                    start=entry.get("start", ""),
                    duration=entry.get("duration", ""),
                ))

    return talks
