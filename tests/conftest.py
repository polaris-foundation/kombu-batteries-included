from unittest.mock import Mock

import pytest
from kombu import Connection, Exchange, Queue
from pytest_mock import MockFixture


@pytest.fixture
def mock_exchange_init(mocker: MockFixture) -> Mock:
    return mocker.patch.object(Exchange, "__init__", return_value=None)


@pytest.fixture
def mock_queue_init(mocker: MockFixture) -> Mock:
    return mocker.patch.object(Queue, "__init__", return_value=None)


@pytest.fixture
def mock_connection_channel(mocker: MockFixture) -> Mock:
    return mocker.patch.object(Connection, "channel")
