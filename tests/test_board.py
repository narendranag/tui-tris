from tuitris.board import COLS, HIDDEN_ROWS, TOTAL_ROWS, VISIBLE_ROWS, Board
from tuitris.tetromino import Piece


def test_empty_board_dimensions():
    b = Board()
    assert len(b.grid) == TOTAL_ROWS
    assert all(len(row) == COLS for row in b.grid)
    assert VISIBLE_ROWS == 20
    assert HIDDEN_ROWS == 2


def test_fits_inside_empty_board():
    b = Board()
    # T piece in rotation 0 at spawn position (col=3) — bounding box rows 0-1, cols 3-6.
    p = Piece("T", row=0, col=3, rot=0)
    assert b.fits(p)


def test_fits_rejects_left_wall():
    b = Board()
    p = Piece("T", row=5, col=-1, rot=0)  # bounding box col -1 — at least one cell is off left wall
    assert not b.fits(p)


def test_fits_rejects_right_wall():
    b = Board()
    # T rotation 0 cells at cols 0,1,2 within bbox — at col=8 they're at 8,9,10 — col 10 off right.
    p = Piece("T", row=5, col=8, rot=0)
    assert not b.fits(p)


def test_fits_rejects_floor():
    b = Board()
    # T rot-0 has a cell at row 1 of its bbox; at row=TOTAL_ROWS-1 that cell falls off the bottom.
    p = Piece("T", row=TOTAL_ROWS - 1, col=3, rot=0)
    assert not b.fits(p)


def test_fits_allows_negative_rows():
    b = Board()
    # Pieces spawning at the top can have bbox rows above 0; allowed as long as cell rows fit.
    p = Piece("I", row=-1, col=3, rot=0)
    assert b.fits(p)


def test_lock_stamps_cells():
    b = Board()
    p = Piece("T", row=18, col=3, rot=0)
    b.lock(p)
    for r, c in p.cells():
        assert b.cell(r, c) == "T"


def test_fits_rejects_overlap_with_locked_cell():
    b = Board()
    p1 = Piece("T", row=18, col=3, rot=0)
    b.lock(p1)
    # Same position again should not fit.
    assert not b.fits(p1)


def test_clear_lines_zero_when_nothing_full():
    b = Board()
    p = Piece("T", row=20, col=3, rot=0)
    b.lock(p)
    assert b.clear_lines() == 0


def test_clear_lines_single_row():
    b = Board()
    # Fill the entire bottom row.
    for c in range(COLS):
        b.grid[TOTAL_ROWS - 1][c] = "I"
    cleared = b.clear_lines()
    assert cleared == 1
    # Everything shifted down one; the (now-empty) top row was filled, leaving bottom empty.
    assert all(cell is None for cell in b.grid[TOTAL_ROWS - 1])


def test_clear_lines_four_rows_tetris():
    b = Board()
    for r in range(TOTAL_ROWS - 4, TOTAL_ROWS):
        for c in range(COLS):
            b.grid[r][c] = "I"
    cleared = b.clear_lines()
    assert cleared == 4
    assert all(all(cell is None for cell in row) for row in b.grid)


def test_clear_lines_partial_row_kept():
    b = Board()
    # Fill bottom row except one cell — must NOT clear.
    for c in range(COLS - 1):
        b.grid[TOTAL_ROWS - 1][c] = "I"
    cleared = b.clear_lines()
    assert cleared == 0
    # The partial row should still be there.
    assert b.grid[TOTAL_ROWS - 1][0] == "I"


def test_clear_lines_shifts_blocks_above_down():
    b = Board()
    # Full bottom row + a single block two rows above.
    for c in range(COLS):
        b.grid[TOTAL_ROWS - 1][c] = "I"
    b.grid[TOTAL_ROWS - 3][5] = "T"
    cleared = b.clear_lines()
    assert cleared == 1
    # The T block should have dropped by one row.
    assert b.grid[TOTAL_ROWS - 2][5] == "T"
    assert b.grid[TOTAL_ROWS - 3][5] is None
