import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.modules.todo.ui.dialogs.create_task.handlers import make_default_task_data
from app.modules.todo.ui.dialogs.states import CreateTaskDialogSG, CreateListDialogSG
from app.core.utils.dialog_serialization import to_dialog_safe

logger = logging.getLogger(__name__)


async def go_create_task(
        _callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Переход в диалог создания задачи")
    message_id = dialog_manager.dialog_data.get("message_id")
    task_text = dialog_manager.dialog_data.get("text")

    if message_id is None or task_text is None:
        raise ValueError("Missing required dialog_data: message_id or text")

    task_data = to_dialog_safe(make_default_task_data(message_id, task_text))
    await dialog_manager.start(
        state=CreateTaskDialogSG.add_task_window,
        data=task_data,
    )


async def go_create_list(
        _callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Переход в диалог создания списка")
    message_id = dialog_manager.dialog_data.get("message_id")
    list_title = dialog_manager.dialog_data.get("text")
    list_data = {"message_id": message_id, "new_list_title": list_title}
    logger.debug("list_data=%s", list_data)
    await dialog_manager.start(
        state=CreateListDialogSG.add_list_window,
        data=list_data,
    )


async def go_cancel(
        callback: CallbackQuery,
        _widget: Button,
        dialog_manager: DialogManager,
):
    logger.debug("Случайное сообщение пользователя")
    message_id = dialog_manager.dialog_data.get("message_id")
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text="Понял! Буду делать вид, что этого сообщения не было 😉",
        reply_to_message_id=message_id,
    )
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def go_settings(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно настроек. Функция %s",
        go_settings.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход в настройки бота"
    )


async def go_features(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно возможностей бота. Функция %s",
        go_features.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет переход к описанию возможностей бота"
    )


async def go_support(
        callback: CallbackQuery,
        _widget: Button,
        _dialog_manager: DialogManager
):
    logger.debug(
        "Заглушка-переход в окно технической поддержки. Функция %s",
        go_support.__name__
    )
    await callback.answer(
        "Когда-нибудь тут будет соединение с технической поддержкой"
    )


async def on_predict_dialog_process_result(
        _start_data,
        result: dict,
        dialog_manager: DialogManager
):
    logger.debug("Выполнение действий при закрытии предыдущего диалога")
    logger.debug("result=%s", result)
    if not result:
        logger.debug("Предыдущий диалог закрыт без возвращения данных")
        return
    logger.debug("Возврат к предыдущему диалогу")
    await dialog_manager.done()
