import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.notifications.webhook_dispatcher import dispatch_pending_events


def test_price_delta_positive():
    """Price increase should produce positive delta."""
    old_price = 100.0
    new_price = 150.0
    delta = round(new_price - old_price, 2)
    assert delta == 50.0
    assert delta > 0


def test_price_delta_negative():
    """Price decrease should produce negative delta."""
    old_price = 200.0
    new_price = 150.0
    delta = round(new_price - old_price, 2)
    assert delta == -50.0
    assert delta < 0


def test_price_delta_zero():
    """Same price should produce zero delta."""
    old_price = 100.0
    new_price = 100.0
    delta = round(new_price - old_price, 2)
    assert delta == 0.0


def test_price_delta_precision():
    """Delta should be rounded to 2 decimal places."""
    old_price = 100.0
    new_price = 133.333333
    delta = round(new_price - old_price, 2)
    assert delta == 33.33


@pytest.mark.asyncio
async def test_dispatch_no_events_runs_cleanly():
    """Dispatcher should exit cleanly when there are no pending events."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("backend.notifications.webhook_dispatcher.AsyncSessionLocal", return_value=mock_cm):
        await dispatch_pending_events()
