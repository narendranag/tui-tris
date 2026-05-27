"""Pure rendering: Game state -> Rich Text. No textual imports."""

from __future__ import annotations

from rich.text import Text

from tuitris.board import COLS, HIDDEN_ROWS
from tuitris.game import Game
from tuitris.tetromino import COLORS, SHAPES, Piece, PieceType, color

CELL_FILLED = "██"
CELL_EMPTY = "  "
CELL_GHOST = "░░"
GHOST_STYLE = "grey35"


def render_board(game: Game) -> Text:
    """Render the visible playfield as a Rich Text block.

    Layers (bottom to top): locked cells, ghost piece, current piece.
    """
    grid = [row[:] for row in game.board.visible_rows()]  # copy of locked cells

    # Overlay ghost piece (only if state is playing — otherwise the ghost is confusing).
    ghost_cells: set[tuple[int, int]] = set()
    if game.state == "playing":
        ghost_row = game.ghost_row()
        ghost = Piece(
            type=game.current.type,
            row=ghost_row,
            col=game.current.col,
            rot=game.current.rot,
        )
        for r, c in ghost.cells():
            vr = r - HIDDEN_ROWS
            if 0 <= vr < len(grid) and 0 <= c < COLS:
                ghost_cells.add((vr, c))

    # Overlay current piece (only if state isn't game_over).
    current_cells: set[tuple[int, int]] = set()
    if game.state != "game_over":
        for r, c in game.current.cells():
            vr = r - HIDDEN_ROWS
            if 0 <= vr < len(grid) and 0 <= c < COLS:
                current_cells.add((vr, c))

    current_color = color(game.current.type)
    text = Text()
    for vr, row in enumerate(grid):
        for c, locked in enumerate(row):
            if (vr, c) in current_cells:
                text.append(CELL_FILLED, style=current_color)
            elif locked is not None:
                text.append(CELL_FILLED, style=color(locked))
            elif (vr, c) in ghost_cells:
                text.append(CELL_GHOST, style=GHOST_STYLE)
            else:
                text.append(CELL_EMPTY, style="on grey11")
        if vr < len(grid) - 1:
            text.append("\n")
    return text


def render_next(piece_type: PieceType) -> Text:
    """Render the next-piece preview as a 4x4 block."""
    cells = SHAPES[piece_type][0]
    style = COLORS[piece_type]
    text = Text()
    for r in range(4):
        for c in range(4):
            if (r, c) in cells:
                text.append(CELL_FILLED, style=style)
            else:
                text.append(CELL_EMPTY)
        if r < 3:
            text.append("\n")
    return text
