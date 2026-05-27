"""Textual front-end: TuitrisApp, BoardWidget, SidebarWidget, key bindings."""

from __future__ import annotations

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static

from tuitris.game import Game
from tuitris.render import render_board, render_next


class BoardWidget(Static):
    DEFAULT_CSS = """
    BoardWidget {
        width: 22;
        height: 22;
        border: solid grey;
        padding: 0;
        content-align: center middle;
    }
    """

    def __init__(self, game: Game, **kwargs) -> None:
        super().__init__(**kwargs)
        self.game = game

    def render(self) -> Text:  # type: ignore[override]
        return render_board(self.game)


class SidebarWidget(Static):
    DEFAULT_CSS = """
    SidebarWidget {
        width: 22;
        height: 22;
        border: solid grey;
        padding: 0 1;
    }
    """

    def __init__(self, game: Game, **kwargs) -> None:
        super().__init__(**kwargs)
        self.game = game

    def render(self) -> Text:  # type: ignore[override]
        text = Text()
        text.append("NEXT\n", style="bold")
        text.append_text(render_next(self.game.next_type))
        text.append("\n\n")
        text.append("SCORE ", style="bold")
        text.append(f"{self.game.score}\n")
        text.append("LEVEL ", style="bold")
        text.append(f"{self.game.level}\n")
        text.append("LINES ", style="bold")
        text.append(f"{self.game.lines_cleared}\n\n")

        if self.game.state == "game_over":
            text.append("GAME OVER\n", style="bold red")
            text.append("R restart\n", style="dim")
            text.append("Q quit\n", style="dim")
        elif self.game.state == "paused":
            text.append("PAUSED\n", style="bold yellow")
            text.append("P resume\n", style="dim")
            text.append("Q quit\n", style="dim")
        else:
            text.append("← → move\n", style="dim")
            text.append("↓ soft drop\n", style="dim")
            text.append("Z X rotate\n", style="dim")
            text.append("⎵ hard drop\n", style="dim")
            text.append("P pause\n", style="dim")
            text.append("Q quit\n", style="dim")
        return text


class TuitrisApp(App):
    CSS = """
    Screen {
        align: center middle;
        background: black;
    }
    Horizontal {
        width: auto;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("left", "move_left", "←", show=False),
        Binding("h", "move_left", "←", show=False),
        Binding("right", "move_right", "→", show=False),
        Binding("l", "move_right", "→", show=False),
        Binding("down", "soft_drop", "↓", show=False),
        Binding("j", "soft_drop", "↓", show=False),
        Binding("space", "hard_drop", "drop", show=False),
        Binding("z", "rotate_ccw", "rotate", show=False),
        Binding("x", "rotate_cw", "rotate", show=False),
        Binding("up", "rotate_cw", "rotate", show=False),
        Binding("k", "rotate_cw", "rotate", show=False),
        Binding("p", "pause", "pause", show=False),
        Binding("r", "restart", "restart", show=False),
        Binding("q", "quit", "quit", show=False),
        Binding("ctrl+c", "quit", "quit", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = Game()
        self._tick_timer = None
        self._last_level = self.game.level

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield BoardWidget(self.game)
            yield SidebarWidget(self.game)

    def on_mount(self) -> None:
        self._start_tick_timer()

    def _start_tick_timer(self) -> None:
        if self._tick_timer is not None:
            self._tick_timer.stop()
        self._tick_timer = self.set_interval(self.game.gravity_seconds(), self._on_tick)

    def _on_tick(self) -> None:
        self.game.tick()
        self._after_change()

    def _after_change(self) -> None:
        for w in self.query(BoardWidget):
            w.refresh()
        for w in self.query(SidebarWidget):
            w.refresh()
        if self.game.level != self._last_level:
            self._last_level = self.game.level
            self._start_tick_timer()

    def action_move_left(self) -> None:
        self.game.move(-1)
        self._after_change()

    def action_move_right(self) -> None:
        self.game.move(1)
        self._after_change()

    def action_soft_drop(self) -> None:
        self.game.soft_drop()
        self._after_change()

    def action_hard_drop(self) -> None:
        self.game.hard_drop()
        self._after_change()

    def action_rotate_cw(self) -> None:
        self.game.rotate(cw=True)
        self._after_change()

    def action_rotate_ccw(self) -> None:
        self.game.rotate(cw=False)
        self._after_change()

    def action_pause(self) -> None:
        if self.game.state in ("playing", "paused"):
            self.game.toggle_pause()
            self._after_change()

    def action_restart(self) -> None:
        if self.game.state == "game_over":
            self.game.restart()
            self._last_level = self.game.level
            self._start_tick_timer()
            self._after_change()


def main() -> None:
    TuitrisApp().run()


if __name__ == "__main__":
    main()
