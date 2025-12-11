import pytest
from aiogram_dialog import Dialog

from app.bot.dialogs import dialogs
from app.bot.dialogs.id_uniqueness_validator import validate_dialog


@pytest.mark.parametrize("dialog", dialogs)
def test_unique_widget_ids_per_window(dialog: Dialog):
    validate_dialog(dialog)
