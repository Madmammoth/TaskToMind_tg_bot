import pytest
from aiogram_dialog import Dialog

from app.modules.todo.ui.dialogs import dialogs
from app.modules.todo.ui.dialogs.id_uniqueness_validator import validate_dialog


@pytest.mark.parametrize("dialog", dialogs)
def test_unique_widget_ids_per_window(dialog: Dialog):
    validate_dialog(dialog)
