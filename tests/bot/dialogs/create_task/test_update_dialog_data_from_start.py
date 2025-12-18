import pytest

from app.bot.dialogs.common.handlers import update_dialog_data_from_start


@pytest.mark.asyncio
async def test_with_start_data(dm):
    dm.start_data = {"1": "1"}

    await update_dialog_data_from_start(dm.start_data, dm)

    assert dm.dialog_data == {"1": "1"}


@pytest.mark.asyncio
async def test_without_start_data(dm):
    await update_dialog_data_from_start(dm.start_data, dm)

    assert dm.dialog_data == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_data", [2, 2.1, "2", False, True, [2], (2,), {2}]
)
async def test_with_start_data(dm, start_data):
    dm.start_data = start_data

    with pytest.raises(ValueError):
        await update_dialog_data_from_start(dm.start_data, dm)  # type: ignore
