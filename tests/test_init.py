import importlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import Mock

import pytest
import pytz as pytz
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from kombu import Connection, Producer
from pytest_mock import MockFixture
from she_logging.request_id import current_request_id

import kombu_batteries_included
from kombu_batteries_included import config, infra


class TestLibrary:
    @pytest.mark.parametrize("rabbitmq_disabled,call_count", [(False, 1), (True, 0)])
    def test_init(
        self,
        mocker: MockFixture,
        monkeypatch: MonkeyPatch,
        rabbitmq_disabled: bool,
        call_count: int,
    ) -> None:
        # Arrange
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=rabbitmq_disabled)
        monkeypatch.setattr(config, "INITIALISED", value=False)
        mock_verify: Mock = mocker.patch.object(infra, "verify_rabbitmq_connection")
        mock_init_error: Mock = mocker.patch.object(
            infra, "init_error_exchange_and_queue"
        )
        mock_init_retry: Mock = mocker.patch.object(
            infra, "init_retry_exchange_and_queue"
        )
        mock_init_task: Mock = mocker.patch.object(infra, "init_task_exchange")

        # Act
        kombu_batteries_included.init()

        # Assert
        assert mock_verify.call_count == call_count
        assert mock_init_error.call_count == call_count
        assert mock_init_retry.call_count == call_count
        assert mock_init_task.call_count == call_count

    @pytest.mark.freeze_time("2019-11-14T00:00:00.000Z")
    @pytest.mark.parametrize("compression", ["bzip2", "zip", None])
    def test_publish_message_enabled(
        self, mocker: MockFixture, monkeypatch: MonkeyPatch, compression: Optional[str]
    ) -> None:
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=False)
        monkeypatch.setattr(config, "RABBITMQ_COMPRESSION", value=compression)
        monkeypatch.setattr(config, "INITIALISED", value=True)
        mock_publish = mocker.patch.object(Producer, "publish")
        routing_key = "dhos.123"
        message_body = {
            "some": "body",
            "once": "told me",
        }
        headers = {"some": "header"}
        kombu_batteries_included.publish_message(
            routing_key=routing_key, body=message_body, headers=headers
        )
        assert mock_publish.call_count == 1
        mock_publish.assert_called_with(
            body=json.dumps(message_body),
            exchange=infra.TASK_EXCHANGE_NAME,
            routing_key=routing_key,
            content_type="application/text",
            compression=compression,
            retry=True,
            timestamp=1573689600,
            correlation_id=current_request_id(),
            headers=headers,
        )

    def test_publish_message_disabled(
        self, mocker: MockFixture, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=True)
        monkeypatch.setattr(config, "INITIALISED", value=True)
        mock_publish = mocker.patch.object(Producer, "publish")
        routing_key = "dhos.123"
        message_body = {"some": "body", "once": "told me"}
        kombu_batteries_included.publish_message(
            routing_key=routing_key, body=message_body
        )
        assert mock_publish.call_count == 0
        assert "Skipping RabbitMQ message publish" in caplog.text

    def test_get_connection_string(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setenv("RABBITMQ_HOST", value="http://somehost")
        monkeypatch.setenv("RABBITMQ_PORT", value="8877")
        monkeypatch.setenv("RABBITMQ_USERNAME", value="test-username")
        monkeypatch.setenv("RABBITMQ_PASSWORD", value="test-password")
        importlib.reload(kombu_batteries_included.config)
        assert (
            kombu_batteries_included.get_connection_string()
            == f"amqp://test-username:test-password@http://somehost:8877//"
        )

    def test_publish_message_with_datetime(
        self, mocker: MockFixture, monkeypatch: MonkeyPatch
    ) -> None:
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=False)
        monkeypatch.setattr(config, "INITIALISED", value=True)
        mock_publish = mocker.patch.object(Producer, "publish")
        routing_key = "dhos.123"
        message_body = {
            "some_datetime": datetime.utcnow(),
        }
        kombu_batteries_included.publish_message(
            routing_key=routing_key, body=message_body
        )
        assert mock_publish.call_count == 1

    def test_publish_message_with_unserializable(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=False)
        monkeypatch.setattr(config, "INITIALISED", value=True)
        message_body = {
            "unserializable": Connection(),
        }
        with pytest.raises(TypeError):
            kombu_batteries_included.publish_message(
                routing_key="something", body=message_body
            )

    def test_publish_not_initialised(
        self, monkeypatch: MonkeyPatch, caplog: LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(config, "RABBITMQ_DISABLED", value=False)
        monkeypatch.setattr(config, "INITIALISED", value=False)
        with pytest.raises(ValueError):
            kombu_batteries_included.publish_message(
                routing_key="something", body={"some": "body"}
            )
        assert "You must init() the library" in caplog.text

    @pytest.mark.parametrize(
        "to_convert,expected",
        [
            (
                datetime(2020, 1, 2, 12, 34, 56, 123456, tzinfo=timezone.utc),
                "2020-01-02T12:34:56.123+00:00",
            ),
            (
                pytz.timezone("America/New_York").localize(
                    datetime(2020, 1, 2, 12, 34, 56, 123456)
                ),
                "2020-01-02T12:34:56.123-05:00",
            ),
            (datetime(2020, 1, 2, 12, 34, 56, 123456), "2020-01-02T12:34:56.123+00:00"),
        ],
    )
    def test_simple_converter(self, to_convert: Any, expected: str) -> None:
        actual = kombu_batteries_included._simple_converter(to_convert)
        assert actual == expected
