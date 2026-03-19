"""Unit tests for ide_ai.app — IdeApp and run()."""

import pytest
from textual.widgets import Footer, Header

from ide_ai.app import IdeApp, run


# ---------------------------------------------------------------------------
# Class-level attribute tests (no async needed)
# ---------------------------------------------------------------------------


def test_app_title():
    assert IdeApp.TITLE == "ide.ai"


def test_app_subtitle():
    assert IdeApp.SUB_TITLE == "AI-powered terminal IDE"


def test_app_css_path():
    assert IdeApp.CSS_PATH == "app.tcss"


def test_app_has_quit_binding():
    """The 'q' key must be bound to the 'quit' action."""
    bindings = {b[0]: b[1] for b in IdeApp.BINDINGS}
    assert "q" in bindings
    assert bindings["q"] == "quit"


def test_run_is_callable():
    assert callable(run)


# ---------------------------------------------------------------------------
# compose() tests — instantiate app and inspect yielded widgets
# ---------------------------------------------------------------------------


def test_app_compose_yields_header():
    widgets = list(IdeApp().compose())
    types = [type(w) for w in widgets]
    assert Header in types


def test_app_compose_yields_footer():
    widgets = list(IdeApp().compose())
    types = [type(w) for w in widgets]
    assert Footer in types


def test_app_compose_widget_order():
    """Header must come before Footer."""
    widgets = list(IdeApp().compose())
    types = [type(w) for w in widgets]
    assert types.index(Header) < types.index(Footer)


def test_app_header_shows_clock():
    """Header must be created with show_clock=True."""
    widgets = list(IdeApp().compose())
    header = next(w for w in widgets if isinstance(w, Header))
    assert header._show_clock is True


# ---------------------------------------------------------------------------
# Integration test — run_test() spins up the full Textual app in headless mode
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_app_runs_headless():
    """App must start and shut down cleanly in headless mode."""
    async with IdeApp().run_test(headless=True) as pilot:
        assert pilot.app.title == "ide.ai"


@pytest.mark.asyncio
async def test_app_quit_binding_exits():
    """Pressing 'q' must trigger the quit action and exit the app."""
    async with IdeApp().run_test(headless=True) as pilot:
        await pilot.press("q")
    # If we reach here without hanging, the quit binding worked
