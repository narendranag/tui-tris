# Session Handoff — 2026-05-27

A working record of what was built in this session and where to pick up next.
Greenfield project at `/Users/narendranag/ai/tuitris`, pushed to
[github.com/narendranag/tui-tris](https://github.com/narendranag/tui-tris) (public, `main` branch).

## What got built

A playable terminal Tetris clone in Python + textual, with high-scores persistence.
"Weekend MVP" scope — standard playable rules, no novel mechanics.

### Stack

- **Runtime:** Python 3.11+ (confirmed working on 3.12).
- **TUI:** textual ≥ 0.80 (currently 8.2.7).
- **Tooling:** uv (env + entry point), pytest + pytest-asyncio, ruff.
- **Install/run:** `uv sync && uv run tuitris`.

### Architecture (model/view firewall)

Pure-Python game modules with **zero textual imports**:

- `src/tuitris/tetromino.py` — `PIECES` table (7 pieces × 4 rotations × 4 offsets in a
  4×4 bounding box), colors, `Piece` dataclass with `moved()` / `rotated()` / `cells()`.
- `src/tuitris/bag.py` — `SevenBag` (shuffle/refill randomizer, seedable).
- `src/tuitris/board.py` — `Board` (10×22 grid: 20 visible + 2 hidden spawn rows),
  `fits()` / `lock()` / `clear_lines()`.
- `src/tuitris/game.py` — `Game` orchestrator: tick, move, rotate (with simple wall
  kicks `(0,0), (0,±1), (0,±2)`), soft/hard drop, ghost row, NES-ish scoring,
  level/gravity, pause, restart, game-over detection.
- `src/tuitris/render.py` — pure `Game → rich.text.Text`. `render_board()` overlays
  locked cells, ghost (faint grey `░░`), and current piece. `render_next()` for the
  preview block.
- `src/tuitris/scores.py` — `HighScore` dataclass + `HighScores` (load/save JSON at
  `~/.tuitris/scores.json`, top 10, `qualifies()`, `insert()`).

Textual-touching modules (only these):

- `src/tuitris/app.py` — `TuitrisApp`, `BoardWidget`, `SidebarWidget`. Owns the
  `Game` and `HighScores`. Drives gravity via `set_interval` (canceled + recreated on
  level change). Game-over hooks into the screens flow.
- `src/tuitris/screens.py` — `InitialsScreen` (3 slots cycling A–Z; ↑/↓ change letter,
  ←/→ switch slot, ↵ submit; `dismiss(initials)`), `HighScoresScreen` (table with
  new-entry highlighted; `r`/↵ restart, `q`/Esc quit; signals via `dismiss(result)`).

### Game-over flow

`_after_change()` watches for `game.state == "game_over"` transitions, gated by
`_game_over_handled` so it only fires once per game.

1. If `scores.qualifies(score)`: push `InitialsScreen` → on submit, build a
   `HighScore` and `scores.insert(entry)` → push `HighScoresScreen` with the new rank.
2. Otherwise: push `HighScoresScreen` directly with `new_rank=None`.
3. From the high-scores screen: `r`/↵ → `_restart_game()` (resets `Game`, clears the
   handled flag, restarts the gravity timer); `q`/Esc → `app.exit()`.

### Tests (45 total, all passing)

- `tests/test_bag.py` — 4 tests: bag returns all 7, refill, peek, determinism with seed.
- `tests/test_board.py` — 13 tests: dimensions, `fits` for walls/floor/overlap,
  `lock`, `clear_lines` for 1/4 line / partial / shifting.
- `tests/test_game.py` — 16 tests: spawn, tick, lock/spawn, movement, drops + scoring,
  rotation, ghost row, gravity speedup, level formula, pause-blocks-actions, line-clear
  scoring, game-over on spawn collision, restart.
- `tests/test_scores.py` — 9 tests: missing file, corrupt JSON, roundtrip, qualifies
  under/over max, insert ranking, trim, persistence, defensive sort on load.
- `tests/test_app_smoke.py` — 3 headless textual tests: basic keys don't crash,
  full game-over → initials → table → restart flow, low-score skips initials.

All tests use `tmp_path` for scores file — none touch the user's real
`~/.tuitris/scores.json`.

### Design decisions worth remembering

- **No SRS rotation** — hard-coded rotation tables + simple wall-kick fallback. Easier
  to reason about, "feels right enough" for casual play.
- **Hidden spawn rows** — board is actually 22 rows; rows 0–1 are above the visible
  area so pieces can spawn off-screen and game-over fires cleanly when the spawn
  collides.
- **Ghost piece styling** — light-shade glyph `░░` in `grey35` (not the piece color,
  which was visually distracting). Knob to tweak is `GHOST_STYLE` in
  `src/tuitris/render.py:8`.
- **No `r` binding on the main app** — restart is only reachable through the
  high-scores screen after game over. Cleaner UX: you always see your final score
  before replaying.
- **Initials default to "AAA"** — Nintendo arcade convention.

## What's NOT built (deferred / out of scope)

- Hold piece (swap current with held).
- Pause menu beyond the sidebar text.
- High-scores viewer accessible *before* dying (e.g. a title screen with `h` to view).
- Configurable controls / theming.
- Sounds (tricky in TUI anyway).
- SRS rotation system.
- Multiplayer / network play.
- Difficulty / starting-level selection.
- Stats beyond score/lines/level (e.g. tetrises, T-spins, pieces dropped).

## Design / planning artifacts

- `/Users/narendranag/.claude/plans/adaptive-chasing-hedgehog.md` — the original
  approved design from the brainstorming → plan-mode workflow. Includes the full
  Context / Architecture / Module layout / Build sequence / Verification sections
  that this implementation was built against.
- This file (`SESSION.md`) — the post-build session record.

## Picking up next session

Likely next moves, in rough order of "would feel good to ship":

1. **Hold piece** — `c` key swaps current with held. UI: a "HOLD" slot under or
   above NEXT in the sidebar. State: `Game.hold_piece: PieceType | None`, plus a
   `_hold_used_this_drop: bool` flag (prevents infinite hold-swap exploit).
2. **Title screen** — first thing on app start. Lets the user see high scores
   before dying, pick starting level, and start a new game. Would mean pushing the
   game-screen as a screen of its own, not the root.
3. **Difficulty / starting level** — pass `start_level` to `Game.__init__`; gravity
   uses that immediately.
4. **Snapshot-test the renderer** — `render_board(game)` is a pure function, so
   freeze a few golden frames as plain-text fixtures and assert against them. Would
   catch regressions in the visual layer that the smoke test can't see.
5. **CHANGELOG.md** — start tracking versions once there's more than one feature
   landing per push.
6. **CI** — GitHub Actions workflow that runs `uv sync` + `uv run pytest` + ruff on
   pushes/PRs.

## Running it

```bash
cd /Users/narendranag/ai/tuitris
uv sync                      # one-time setup
uv run tuitris               # play
uv run pytest                # run tests (1.9s)
uv run ruff check src tests  # lint
uv run ruff format src tests # format
```

## Caveat

The textual layer has been verified to boot and process input via headless
`App.run_test()` pilot tests — **but not interactively played**. The smoke tests
cover the game-over → initials → high-scores → restart flow programmatically, but
visual issues (cell aspect ratio in a given terminal font, color readability,
spacing in the sidebar) can only be caught by actually launching the app.

If something looks off, likely candidates:

- Cell width — `CELL_FILLED = "██"` in `render.py`. Some fonts render these
  narrower than expected; swap to `▓▓` or two spaces with a colored background if
  the board looks too squished.
- Sidebar width — fixed at 22 columns in `SidebarWidget.DEFAULT_CSS`. Tighten if
  things wrap, widen if the controls section gets clipped.
- High-scores modal width — fixed at 42 columns in
  `HighScoresScreen.CSS#scores-box`. Same deal.
