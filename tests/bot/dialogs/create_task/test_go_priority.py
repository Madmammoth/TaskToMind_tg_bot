import pytest

from app.bot.dialogs.create_task.handlers import go_priority
from tests.bot.mocks import MockButton


@pytest.mark.asyncio
async def test_priority_change(dm, mock_callback):
    btn = MockButton(widget_id="high", text="Высокий")

    await go_priority(mock_callback, btn, dm)

    assert dm.dialog_data["priority"].value == "high"
    assert dm.dialog_data["priority_label"] == "Высокий"
