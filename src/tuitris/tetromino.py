"""Tetromino shapes, rotation tables, and colors.

Each piece has 4 rotation states. A rotation is a frozenset of (row, col)
offsets within a 4x4 bounding box. A piece's world position is the (row, col)
of that bounding box's top-left corner.
"""

from __future__ import annotations

from dataclasses import dataclass

PieceType = str  # one of "I", "O", "T", "S", "Z", "J", "L"

PIECE_TYPES: tuple[PieceType, ...] = ("I", "O", "T", "S", "Z", "J", "L")

# Rich color names per piece type.
COLORS: dict[PieceType, str] = {
    "I": "cyan",
    "O": "yellow",
    "T": "magenta",
    "S": "green",
    "Z": "red",
    "J": "blue",
    "L": "dark_orange",
}

# Each piece: 4 rotation states, each a frozenset of (row, col) offsets.
SHAPES: dict[PieceType, tuple[frozenset[tuple[int, int]], ...]] = {
    "I": (
        frozenset({(1, 0), (1, 1), (1, 2), (1, 3)}),
        frozenset({(0, 2), (1, 2), (2, 2), (3, 2)}),
        frozenset({(2, 0), (2, 1), (2, 2), (2, 3)}),
        frozenset({(0, 1), (1, 1), (2, 1), (3, 1)}),
    ),
    "O": (
        frozenset({(0, 1), (0, 2), (1, 1), (1, 2)}),
        frozenset({(0, 1), (0, 2), (1, 1), (1, 2)}),
        frozenset({(0, 1), (0, 2), (1, 1), (1, 2)}),
        frozenset({(0, 1), (0, 2), (1, 1), (1, 2)}),
    ),
    "T": (
        frozenset({(0, 1), (1, 0), (1, 1), (1, 2)}),
        frozenset({(0, 1), (1, 1), (1, 2), (2, 1)}),
        frozenset({(1, 0), (1, 1), (1, 2), (2, 1)}),
        frozenset({(0, 1), (1, 0), (1, 1), (2, 1)}),
    ),
    "S": (
        frozenset({(0, 1), (0, 2), (1, 0), (1, 1)}),
        frozenset({(0, 1), (1, 1), (1, 2), (2, 2)}),
        frozenset({(1, 1), (1, 2), (2, 0), (2, 1)}),
        frozenset({(0, 0), (1, 0), (1, 1), (2, 1)}),
    ),
    "Z": (
        frozenset({(0, 0), (0, 1), (1, 1), (1, 2)}),
        frozenset({(0, 2), (1, 1), (1, 2), (2, 1)}),
        frozenset({(1, 0), (1, 1), (2, 1), (2, 2)}),
        frozenset({(0, 1), (1, 0), (1, 1), (2, 0)}),
    ),
    "J": (
        frozenset({(0, 0), (1, 0), (1, 1), (1, 2)}),
        frozenset({(0, 1), (0, 2), (1, 1), (2, 1)}),
        frozenset({(1, 0), (1, 1), (1, 2), (2, 2)}),
        frozenset({(0, 1), (1, 1), (2, 0), (2, 1)}),
    ),
    "L": (
        frozenset({(0, 2), (1, 0), (1, 1), (1, 2)}),
        frozenset({(0, 1), (1, 1), (2, 1), (2, 2)}),
        frozenset({(1, 0), (1, 1), (1, 2), (2, 0)}),
        frozenset({(0, 0), (0, 1), (1, 1), (2, 1)}),
    ),
}


@dataclass(frozen=True)
class Piece:
    """A tetromino in flight: type, world position, and rotation index."""

    type: PieceType
    row: int
    col: int
    rot: int = 0

    def cells(self) -> frozenset[tuple[int, int]]:
        """World-space (row, col) cells this piece currently occupies."""
        return frozenset((self.row + r, self.col + c) for r, c in SHAPES[self.type][self.rot])

    def moved(self, drow: int, dcol: int) -> Piece:
        return Piece(self.type, self.row + drow, self.col + dcol, self.rot)

    def rotated(self, cw: bool) -> Piece:
        step = 1 if cw else -1
        return Piece(self.type, self.row, self.col, (self.rot + step) % 4)


def color(piece_type: PieceType) -> str:
    return COLORS[piece_type]


def shape(piece_type: PieceType, rot: int = 0) -> frozenset[tuple[int, int]]:
    return SHAPES[piece_type][rot % 4]
