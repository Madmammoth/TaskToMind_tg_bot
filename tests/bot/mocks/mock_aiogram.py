from datetime import datetime, timezone
from typing import Optional

from aiogram.types import Message, Chat, User


class MockBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(
            self,
            chat_id: int,
            text: str,
            reply_to_message_id: Optional[int] = None,
    ):
        self.sent_messages.append({
            "chat": chat_id,
            "text": text,
            "reply_to": reply_to_message_id,
        })


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class FakeEvent:
    def __init__(self):
        self.from_user = FakeUser(42)


class MockMessage(Message):
    def __init__(self, message_id: int, text: str):
        super().__init__(
            message_id=message_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=1, type="private"),
            from_user=User(id=1, is_bot=False, first_name="F"),
            text=text,
        )


class MockCallbackQuery:
    def __init__(self, data: str = ""):
        self.id = "1"
        self.data = data
        self.from_user = User(id=1, is_bot=False, first_name="F")
        self.message = None
        self.bot = MockBot()

    async def answer(self, text: str = "", **_):
        pass
