import pytest

from tests.bot.mocks import MockDialogManager, MockMessage, MockCallbackQuery


@pytest.fixture
def dm():
    return MockDialogManager()


@pytest.fixture
def mock_message():
    return MockMessage(message_id=10, text="Test task")


@pytest.fixture
def mock_callback():
    return MockCallbackQuery()
