# tuitris

A Tetris-style TUI game in Python + [textual](https://github.com/Textualize/textual).

## Install

```bash
uv sync
```

## Run

```bash
uv run tuitris
# or
uv run python -m tuitris
```

## Controls

| Key                  | Action                          |
|----------------------|---------------------------------|
| `←` / `h`            | Move left                       |
| `→` / `l`            | Move right                      |
| `↓` / `j`            | Soft drop (+1 per cell)         |
| `Space`              | Hard drop (+2 per cell)         |
| `x` / `↑` / `k`      | Rotate clockwise                |
| `z`                  | Rotate counter-clockwise        |
| `p`                  | Pause / resume                  |
| `q` / `Ctrl+C`       | Quit                            |

### After game over

| Key                  | Action                          |
|----------------------|---------------------------------|
| `↑` / `↓`            | Cycle current initial A–Z       |
| `←` / `→`            | Move between initial slots      |
| `↵` (Enter)          | Submit initials                 |
| `r` / `↵`            | Play again (from scores table)  |
| `q` / `Esc`          | Quit (from scores table)        |

## Rules

- 10 × 20 playfield, 7 standard tetrominoes, 7-bag randomizer.
- Standard NES-ish scoring: 1/2/3/4 lines = 40 / 100 / 300 / 1200, all × (level + 1).
- Level increases every 10 lines cleared. Gravity speeds up each level.
- Wall kicks: on rotation, tries `(0, 0), (0, ±1), (0, ±2)` until one fits.

## High scores

Top 10 scores are persisted in `~/.tuitris/scores.json`. After every game, if your
score qualifies, you get a Nintendo-style 3-letter initials entry; then the full
table is shown with your row highlighted.

## Development

```bash
uv run pytest                    # run tests
uv run ruff check src tests      # lint
uv run ruff format src tests     # format
```

## Architecture

Pure-Python game model (`tetromino`, `bag`, `board`, `game`, `render`) with zero textual
imports — only `app.py` touches textual. All game rules are unit-tested; the textual layer
has a headless smoke test.

## License

MIT
