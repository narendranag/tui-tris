"""7-bag randomizer: each cycle returns all 7 piece types in random order."""

from __future__ import annotations

import random
from collections import deque

from tuitris.tetromino import PIECE_TYPES, PieceType


class SevenBag:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._queue: deque[PieceType] = deque()
        self._refill()

    def _refill(self) -> None:
        bag = list(PIECE_TYPES)
        self._rng.shuffle(bag)
        self._queue.extend(bag)

    def next(self) -> PieceType:
        if not self._queue:
            self._refill()
        return self._queue.popleft()

    def peek(self) -> PieceType:
        if not self._queue:
            self._refill()
        return self._queue[0]
