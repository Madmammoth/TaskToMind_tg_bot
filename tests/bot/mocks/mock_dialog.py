from typing import Any


class MockDialogManager:
    def __init__(self):
        self.dialog_data: dict[str, Any] = {}
        self.middleware_data: dict[str, Any] = {}
        self.result: Any = None
        self.finished: bool = False
        self.last_state = None

    async def done(self, result: Any = None, **_):
        self.result = result
        self.finished = True

    async def switch_to(self, state, **_):
        self.last_state = state


class MockSubManager:
    def __init__(self, manager: MockDialogManager, item_id: Any):
        self.manager = manager
        self.item_id = item_id


class MockText:
    def __init__(self, text: str):
        self._text = text

    async def render_text(self, data, manager):
        return self._text


class MockButton:
    def __init__(self, widget_id: str, text: str = ""):
        self.widget_id = widget_id
        self.text = MockText(text)

    async def render_text(self, data, manager):
        return self.text or ""
