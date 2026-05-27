"""The playfield: a 10-column grid with 2 hidden rows above 20 visible rows."""

from __future__ import annotations

from tuitris.tetromino import Piece, PieceType

COLS = 10
VISIBLE_ROWS = 20
HIDDEN_ROWS = 2
TOTAL_ROWS = VISIBLE_ROWS + HIDDEN_ROWS


class Board:
    def __init__(self) -> None:
        self.grid: list[list[PieceType | None]] = [[None] * COLS for _ in range(TOTAL_ROWS)]

    def fits(self, piece: Piece) -> bool:
        """True if the piece can occupy its current cells without overlap or out-of-bounds."""
        for r, c in piece.cells():
            if c < 0 or c >= COLS:
                return False
            if r >= TOTAL_ROWS:
                return False
            # Allow negative rows (above the board) — pieces can spawn partially off-screen.
            if r < 0:
                continue
            if self.grid[r][c] is not None:
                return False
        return True

    def lock(self, piece: Piece) -> None:
        """Stamp the piece's cells onto the grid. No collision check."""
        for r, c in piece.cells():
            if 0 <= r < TOTAL_ROWS and 0 <= c < COLS:
                self.grid[r][c] = piece.type

    def clear_lines(self) -> int:
        """Remove full rows, shift everything above down. Return count cleared."""
        kept = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = TOTAL_ROWS - len(kept)
        empty = [[None] * COLS for _ in range(cleared)]
        self.grid = empty + kept
        return cleared

    def cell(self, row: int, col: int) -> PieceType | None:
        return self.grid[row][col]

    def visible_rows(self) -> list[list[PieceType | None]]:
        return self.grid[HIDDEN_ROWS:]
