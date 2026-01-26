import pytest

from app.bot.dialogs.create_task.handlers import go_priority
from tests.bot.mocks import MockButton


@pytest.mark.asyncio
async def test_priority_change(fake_dialog_manager, mock_callback):
    btn = MockButton(widget_id="high", text="Высокий")

    await go_priority(mock_callback, btn, fake_dialog_manager)  # noqa

    assert fake_dialog_manager.dialog_data["priority"] == {'__enum__': 'LevelEnum.HIGH'}
    assert fake_dialog_manager.dialog_data["priority_label"] == "Высокий"
