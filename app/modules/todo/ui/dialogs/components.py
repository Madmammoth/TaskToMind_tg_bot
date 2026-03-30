import logging

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput, \
    TextInput

from app.modules.todo.ui.dialogs.states import PredictSG

logger = logging.getLogger(__name__)


async def default_text_input_handler(
        message: Message,
        _widget: ManagedTextInput,
        dialog_manager: DialogManager,
        _text: str,
):
    logger.debug("Переход к окну определения смысла сообщения пользователя")
    return_to = dialog_manager.current_context().state.state
    data = {
        "message_id": message.message_id,
        "text": message.html_text,
        "return_to": return_to,
    }
    await dialog_manager.start(
        state=PredictSG.predict_window,
        data=data,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def default_not_text_input_handler(
        message: Message,
        _widget: MessageInput,
        dialog_manager: DialogManager,
):
    logger.debug("Реакция на нетекстовое сообщение пользователя")
    await message.answer("Пожалуйста, пользуйся кнопками 🙂")
    await dialog_manager.show(ShowMode.DELETE_AND_SEND)
    dialog_manager.show_mode = ShowMode.NO_UPDATE


class WindowWithInput(Window):
    def __init__(
            self,
            *widgets,
            text_input_handler=default_text_input_handler,
            not_text_input_handler=default_not_text_input_handler,
            **kwargs
    ):
        input_widgets = [
            TextInput(id="text_input", on_success=text_input_handler),
            MessageInput(not_text_input_handler),
        ]
        widgets = (*widgets, *input_widgets)
        super().__init__(*widgets, **kwargs)


class WindowWithoutInput(Window):
    def __init__(
            self,
            *widgets,
            not_text_input_handler=default_not_text_input_handler,
            **kwargs
    ):
        input_widget = MessageInput(not_text_input_handler)
        widgets = (*widgets, input_widget)
        super().__init__(*widgets, **kwargs)
