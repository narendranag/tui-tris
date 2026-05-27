"""Game orchestrator: drives gravity, movement, rotation, scoring, and level."""

from __future__ import annotations

from typing import Literal

from tuitris.bag import SevenBag
from tuitris.board import Board
from tuitris.tetromino import Piece, PieceType

GameState = Literal["playing", "paused", "game_over"]

SPAWN_ROW = 0
SPAWN_COL = 3

# Score per number of lines cleared, multiplied by (level + 1).
LINE_SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}

# Kick offsets tried after a rotation, in order. First (0, 0) is the un-shifted rotation.
KICK_OFFSETS = ((0, 0), (0, -1), (0, 1), (0, -2), (0, 2))


class Game:
    def __init__(self, seed: int | None = None) -> None:
        self.board = Board()
        self.bag = SevenBag(seed=seed)
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.state: GameState = "playing"
        self.current: Piece = self._spawn_piece(self.bag.next())
        self.next_type: PieceType = self.bag.next()
        # If the spawned piece doesn't fit, game is over immediately.
        if not self.board.fits(self.current):
            self.state = "game_over"

    def _spawn_piece(self, piece_type: PieceType) -> Piece:
        return Piece(type=piece_type, row=SPAWN_ROW, col=SPAWN_COL, rot=0)

    def gravity_seconds(self) -> float:
        return max(0.05, 0.5 * (0.85 ** (self.level - 1)))

    def tick(self) -> None:
        """Gravity step: move current down 1, or lock if it can't."""
        if self.state != "playing":
            return
        moved = self.current.moved(1, 0)
        if self.board.fits(moved):
            self.current = moved
        else:
            self._lock_and_spawn()

    def move(self, dcol: int) -> None:
        if self.state != "playing":
            return
        candidate = self.current.moved(0, dcol)
        if self.board.fits(candidate):
            self.current = candidate

    def soft_drop(self) -> None:
        if self.state != "playing":
            return
        moved = self.current.moved(1, 0)
        if self.board.fits(moved):
            self.current = moved
            self.score += 1
        else:
            self._lock_and_spawn()

    def hard_drop(self) -> None:
        if self.state != "playing":
            return
        distance = 0
        while True:
            moved = self.current.moved(1, 0)
            if not self.board.fits(moved):
                break
            self.current = moved
            distance += 1
        self.score += 2 * distance
        self._lock_and_spawn()

    def rotate(self, cw: bool = True) -> None:
        if self.state != "playing":
            return
        rotated = self.current.rotated(cw)
        for drow, dcol in KICK_OFFSETS:
            candidate = rotated.moved(drow, dcol)
            if self.board.fits(candidate):
                self.current = candidate
                return

    def ghost_row(self) -> int:
        """Row where the current piece would land if hard-dropped right now."""
        ghost = self.current
        while True:
            moved = ghost.moved(1, 0)
            if not self.board.fits(moved):
                return ghost.row
            ghost = moved

    def toggle_pause(self) -> None:
        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"

    def restart(self) -> None:
        self.board = Board()
        self.bag = SevenBag()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.state = "playing"
        self.current = self._spawn_piece(self.bag.next())
        self.next_type = self.bag.next()
        if not self.board.fits(self.current):
            self.state = "game_over"

    def _lock_and_spawn(self) -> None:
        self.board.lock(self.current)
        cleared = self.board.clear_lines()
        if cleared:
            self.score += LINE_SCORES[cleared] * (self.level + 1)
            self.lines_cleared += cleared
            self.level = 1 + (self.lines_cleared // 10)
        self.current = self._spawn_piece(self.next_type)
        self.next_type = self.bag.next()
        if not self.board.fits(self.current):
            self.state = "game_over"
