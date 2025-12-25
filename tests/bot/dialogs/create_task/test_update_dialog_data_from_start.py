import pytest

from app.bot.dialogs.common.handlers import update_dialog_data_from_start


@pytest.mark.asyncio
async def test_with_start_data(fake_dialog_manager):
    fake_dialog_manager.start_data = {"1": "1"}

    await update_dialog_data_from_start(fake_dialog_manager.start_data, fake_dialog_manager)

    assert fake_dialog_manager.dialog_data == {"1": "1"}


@pytest.mark.asyncio
async def test_without_start_data(fake_dialog_manager):
    await update_dialog_data_from_start(fake_dialog_manager.start_data, fake_dialog_manager)

    assert fake_dialog_manager.dialog_data == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_data", [2, 2.1, "2", False, True, [2], (2,), {2}]
)
async def test_with_start_data(fake_dialog_manager, start_data):
    fake_dialog_manager.start_data = start_data

    with pytest.raises(ValueError):
        await update_dialog_data_from_start(fake_dialog_manager.start_data, fake_dialog_manager)  # type: ignore
