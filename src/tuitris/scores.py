"""High-scores persistence: JSON file at ~/.tuitris/scores.json by default."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_SCORES_PATH = Path.home() / ".tuitris" / "scores.json"
MAX_SCORES = 10


@dataclass
class HighScore:
    initials: str
    score: int
    lines: int
    level: int

    def to_dict(self) -> dict:
        return {
            "initials": self.initials,
            "score": self.score,
            "lines": self.lines,
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, d: dict) -> HighScore:
        return cls(
            initials=str(d.get("initials", "AAA"))[:3],
            score=int(d.get("score", 0)),
            lines=int(d.get("lines", 0)),
            level=int(d.get("level", 1)),
        )


@dataclass
class HighScores:
    path: Path = DEFAULT_SCORES_PATH
    entries: list[HighScore] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path = DEFAULT_SCORES_PATH) -> HighScores:
        if not path.exists():
            return cls(path=path, entries=[])
        try:
            data = json.loads(path.read_text())
            entries = [HighScore.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            entries = []
        entries.sort(key=lambda e: e.score, reverse=True)
        return cls(path=path, entries=entries[:MAX_SCORES])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([e.to_dict() for e in self.entries], indent=2))

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.entries) < MAX_SCORES:
            return True
        return score > self.entries[-1].score

    def insert(self, entry: HighScore) -> int:
        """Insert entry, sort (stable: ties keep earlier first), trim to top N, save.

        Returns the 0-indexed rank of the new entry, or -1 if it didn't make the cut.
        """
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.score, reverse=True)
        self.entries = self.entries[:MAX_SCORES]
        self.save()
        for i, e in enumerate(self.entries):
            if e is entry:
                return i
        return -1
