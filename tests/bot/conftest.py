from unittest.mock import AsyncMock

import pytest

from tests.bot.mocks import FakeDialogManager, MockMessage, MockCallbackQuery


@pytest.fixture
def fake_dialog_manager():
    return FakeDialogManager()


@pytest.fixture
def mock_message():
    return MockMessage(message_id=10, text="Test task\nTest description")


@pytest.fixture
def mock_callback():
    return MockCallbackQuery()


@pytest.fixture
def mock_session():
    return AsyncMock()
