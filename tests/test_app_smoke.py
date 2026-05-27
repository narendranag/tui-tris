"""Headless smoke tests: boot the app, drive it through inputs, verify no exceptions."""

import pytest

from tuitris.app import TuitrisApp


@pytest.mark.asyncio
async def test_app_boots_and_handles_basic_keys(tmp_path):
    app = TuitrisApp(scores_path=tmp_path / "scores.json")
    async with app.run_test() as pilot:
        await pilot.pause()
        for key in ("left", "right", "down", "x", "z", "space", "p", "p"):
            await pilot.press(key)
        await pilot.pause()
        assert app.game is not None


@pytest.mark.asyncio
async def test_game_over_shows_initials_and_high_scores(tmp_path):
    app = TuitrisApp(scores_path=tmp_path / "scores.json")
    async with app.run_test() as pilot:
        await pilot.pause()
        # Force a game over.
        app.game.score = 500
        app.game.state = "game_over"
        app._game_over_handled = False
        app._after_change()
        await pilot.pause()
        # Initials screen should be on top.
        from tuitris.screens import InitialsScreen

        assert isinstance(app.screen, InitialsScreen)
        # Cycle the first letter once down (A -> B), advance slot, submit.
        await pilot.press("down")
        await pilot.press("right")
        await pilot.press("right")
        await pilot.press("enter")
        await pilot.pause()
        # High scores screen now.
        from tuitris.screens import HighScoresScreen

        assert isinstance(app.screen, HighScoresScreen)
        # The new entry should be saved.
        assert len(app.scores.entries) == 1
        assert app.scores.entries[0].initials == "BAA"
        # Press R to restart.
        await pilot.press("r")
        await pilot.pause()
        assert app.game.state == "playing"


@pytest.mark.asyncio
async def test_game_over_skips_initials_when_score_is_zero(tmp_path):
    app = TuitrisApp(scores_path=tmp_path / "scores.json")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.game.score = 0
        app.game.state = "game_over"
        app._game_over_handled = False
        app._after_change()
        await pilot.pause()
        from tuitris.screens import HighScoresScreen, InitialsScreen

        # Score 0 doesn't qualify — should go straight to high-scores screen.
        assert not isinstance(app.screen, InitialsScreen)
        assert isinstance(app.screen, HighScoresScreen)
