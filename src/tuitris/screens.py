"""Modal screens: Nintendo-style initials entry, and high-scores table."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static

from tuitris.scores import HighScores

ALPHABET_SIZE = 26


class InitialsScreen(ModalScreen[str]):
    """Three slots cycling A-Z. ↑/↓ change letter, ←/→ switch slot, ↵ submit."""

    CSS = """
    InitialsScreen {
        align: center middle;
    }
    #initials-box {
        width: 38;
        height: 13;
        border: heavy green;
        background: black;
        padding: 1 2;
        content-align: center middle;
    }
    """

    BINDINGS = [
        Binding("up", "letter_up", "↑", show=False),
        Binding("k", "letter_up", "↑", show=False),
        Binding("down", "letter_down", "↓", show=False),
        Binding("j", "letter_down", "↓", show=False),
        Binding("left", "slot_left", "←", show=False),
        Binding("h", "slot_left", "←", show=False),
        Binding("right", "slot_right", "→", show=False),
        Binding("l", "slot_right", "→", show=False),
        Binding("enter", "submit", "submit", show=False),
    ]

    def __init__(self, score: int) -> None:
        super().__init__()
        self.score = score
        self.letters = ["A", "A", "A"]
        self.slot = 0

    def compose(self) -> ComposeResult:
        yield Static(id="initials-box")

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        text = Text()
        text.append("NEW HIGH SCORE\n", style="bold yellow")
        text.append(f"{self.score}\n\n", style="bold")
        text.append("ENTER YOUR INITIALS\n\n", style="dim")
        for i, letter in enumerate(self.letters):
            style = "reverse bold" if i == self.slot else "bold"
            text.append(f"  {letter}  ", style=style)
        text.append("\n\n")
        text.append("↑↓ change   ←→ slot   ↵ submit", style="dim")
        self.query_one("#initials-box", Static).update(text)

    def _cycle(self, delta: int) -> None:
        cur = self.letters[self.slot]
        new_idx = (ord(cur) - ord("A") + delta) % ALPHABET_SIZE
        self.letters[self.slot] = chr(new_idx + ord("A"))
        self._refresh()

    def action_letter_up(self) -> None:
        self._cycle(-1)

    def action_letter_down(self) -> None:
        self._cycle(1)

    def action_slot_left(self) -> None:
        self.slot = (self.slot - 1) % 3
        self._refresh()

    def action_slot_right(self) -> None:
        self.slot = (self.slot + 1) % 3
        self._refresh()

    def action_submit(self) -> None:
        self.dismiss("".join(self.letters))


class HighScoresScreen(ModalScreen[str]):
    """Show the top-N table. Dismisses with 'restart' or 'quit' to signal the app."""

    CSS = """
    HighScoresScreen {
        align: center middle;
    }
    #scores-box {
        width: 42;
        height: auto;
        border: heavy yellow;
        background: black;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("r", "restart", "restart", show=False),
        Binding("enter", "restart", "restart", show=False),
        Binding("q", "quit", "quit", show=False),
        Binding("escape", "quit", "quit", show=False),
    ]

    def __init__(self, scores: HighScores, new_rank: int | None = None) -> None:
        super().__init__()
        self.scores = scores
        self.new_rank = new_rank

    def compose(self) -> ComposeResult:
        yield Static(id="scores-box")

    def on_mount(self) -> None:
        text = Text()
        text.append("HIGH SCORES\n\n", style="bold yellow")
        if not self.scores.entries:
            text.append("  (no scores yet)\n\n", style="dim")
        else:
            for i, e in enumerate(self.scores.entries):
                is_new = i == self.new_rank
                row_style = "bold yellow" if is_new else ""
                marker = "▸" if is_new else " "
                text.append(f"{marker} {i + 1:>2}.  ", style=row_style)
                text.append(f"{e.initials}", style=(row_style + " bold").strip())
                text.append(f"   {e.score:>8}\n", style=row_style)
        text.append("\nR/↵ play again   Q quit", style="dim")
        self.query_one("#scores-box", Static).update(text)

    def action_restart(self) -> None:
        self.dismiss("restart")

    def action_quit(self) -> None:
        self.dismiss("quit")
