from unittest.mock import Mock

import pytest
from kombu import Connection, Exchange, Queue
from pytest_mock import MockFixture

from kombu_batteries_included import infra


@pytest.mark.usefixtures("mock_exchange_init", "mock_queue_init")
class TestInfra:
    def test_verify_rabbitmq_connection_success(
        self, mock_connection_channel: Mock
    ) -> None:
        infra.verify_rabbitmq_connection(Connection())
        assert mock_connection_channel.call_count == 1

    def test_verify_rabbitmq_connection_failure(
        self, mock_connection_channel: Mock
    ) -> None:
        mock_connection_channel.side_effect = ConnectionRefusedError()
        with pytest.raises(ConnectionRefusedError):
            infra.verify_rabbitmq_connection(Connection())
        assert mock_connection_channel.call_count == 1

    def test_init_error_exchange_and_queue(self, mocker: MockFixture) -> None:
        mock_exchange_declare: Mock = mocker.patch.object(Exchange, "declare")
        mock_queue_declare: Mock = mocker.patch.object(Queue, "declare")
        infra.init_error_exchange_and_queue(Connection())
        assert mock_exchange_declare.call_count == 1
        assert mock_queue_declare.call_count == 1

    def test_init_retry_exchange_and_queue(self, mocker: MockFixture) -> None:
        mock_exchange_declare: Mock = mocker.patch.object(Exchange, "declare")
        mock_queue_declare: Mock = mocker.patch.object(Queue, "declare")
        infra.init_retry_exchange_and_queue(Connection())
        assert mock_exchange_declare.call_count == 1
        assert mock_queue_declare.call_count == 1

    def test_init_task_exchange(self, mocker: MockFixture) -> None:
        mock_exchange_declare: Mock = mocker.patch.object(Exchange, "declare")
        infra.init_task_exchange(Connection())
        assert mock_exchange_declare.call_count == 1
