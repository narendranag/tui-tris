"""Headless smoke test: boot the app, send a few keys, verify no exceptions."""

import pytest

from tuitris.app import TuitrisApp


@pytest.mark.asyncio
async def test_app_boots_and_handles_basic_keys():
    app = TuitrisApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Send a series of inputs — none should crash.
        await pilot.press("left")
        await pilot.press("right")
        await pilot.press("down")
        await pilot.press("x")
        await pilot.press("z")
        await pilot.press("space")
        await pilot.press("p")
        await pilot.press("p")
        await pilot.pause()
        assert app.game is not None
