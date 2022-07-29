import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from kombu import Connection, Producer
from she_logging import logger
from she_logging.request_id import current_request_id

from kombu_batteries_included import config, infra


def init() -> None:
    """
    Initialises and verifies the RabbitMQ connection, and creates infrastructure
    if absent (exchanges, and retry/error queues).
    """
    if config.RABBITMQ_DISABLED:
        logger.debug("Skipping RabbitMQ initialisation due to config")
        return
    with Connection(config.RABBITMQ_CONNECTION_STRING) as conn:
        logger.info("Initialising RabbitMQ connection")
        infra.verify_rabbitmq_connection(conn)
        logger.info("Initialising RabbitMQ infrastructure")
        infra.init_error_exchange_and_queue(conn)
        infra.init_retry_exchange_and_queue(conn)
        infra.init_task_exchange(conn)
        config.INITIALISED = True


def publish_message(
    routing_key: str, body: Union[Dict, List], headers: Optional[Dict[str, Any]] = None
) -> None:
    """
    Publishes a message to the task exchange with the provided routing key, message body, and (optional) headers.
    """
    if config.RABBITMQ_DISABLED:
        logger.debug("Skipping RabbitMQ message publish due to config")
        return
    if not config.INITIALISED:
        logger.error("You must init() the library before attempting to publish")
        raise ValueError("kombu-batteries-included has not been initialised")
    with Connection(config.RABBITMQ_CONNECTION_STRING) as conn:
        producer: Producer = Producer(conn)
        timestamp = int(time.time())
        correlation_id = current_request_id()

        message_body: str = json.dumps(body, default=_simple_converter)
        logger.debug(
            "Publishing %s message", routing_key, extra={"message_body": message_body}
        )
        producer.publish(
            body=message_body,
            exchange=infra.TASK_EXCHANGE_NAME,
            routing_key=routing_key,
            content_type="application/text",
            compression=config.RABBITMQ_COMPRESSION,
            retry=True,
            timestamp=timestamp,
            correlation_id=correlation_id,
            headers=headers,
        )


def get_connection_string() -> str:
    """
    Returns a string designed to be used to initialise a kombu Connection object.
    """
    return config.RABBITMQ_CONNECTION_STRING


def _simple_converter(o: Any) -> str:
    if isinstance(o, datetime):
        if o.tzinfo is None:
            o = o.replace(tzinfo=timezone.utc)
        return o.isoformat(timespec="milliseconds")
    raise TypeError(f"Cannot encode {type(o)} to JSON")
