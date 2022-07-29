from kombu import Connection, Exchange, Queue
from she_logging import logger

TASK_EXCHANGE_NAME = "dhos"
TASK_EXCHANGE_TYPE = "topic"
RETRY_EXCHANGE_NAME = "dhos-retry"
RETRY_EXCHANGE_TYPE = "fanout"
RETRY_QUEUE_NAME = "retry"
DLX_EXCHANGE_NAME = "dhos-dlx"
DLX_EXCHANGE_TYPE = "fanout"
ERROR_QUEUE_NAME = "errors"


def verify_rabbitmq_connection(conn: Connection) -> None:
    """
    Check that we can connect by attempting to create a channel. If we don't do this,
    the app will hang when we try to initialise infrastructure without a working connection.
    """
    logger.info("Verifying RabbitMQ connection")
    try:
        conn.channel()
    except ConnectionRefusedError:
        logger.error("Failed to connect to RabbitMQ")
        raise
    logger.debug("Successfully connected to RabbitMQ")


def init_error_exchange_and_queue(conn: Connection) -> None:
    logger.info("Initialising DLX exchange")
    dlx_exchange: Exchange = Exchange(
        DLX_EXCHANGE_NAME, type=DLX_EXCHANGE_TYPE, channel=conn, durable=True
    )
    dlx_exchange.declare()
    logger.info("Initialising error queue")
    error_queue: Queue = Queue(
        ERROR_QUEUE_NAME, exchange=dlx_exchange, channel=conn, durable=True
    )
    error_queue.declare()


def init_retry_exchange_and_queue(conn: Connection) -> None:
    logger.info("Initialising retry exchange")
    retry_exchange: Exchange = Exchange(
        RETRY_EXCHANGE_NAME, type=RETRY_EXCHANGE_TYPE, channel=conn, durable=True
    )
    logger.info("Initialising retry queue")
    arguments = {
        "x-message-ttl": 60000,
        "x-dead-letter-exchange": TASK_EXCHANGE_NAME,
        "x-queue-mode": "default",
    }
    retry_exchange.declare()
    retry_queue: Queue = Queue(
        RETRY_QUEUE_NAME,
        exchange=retry_exchange,
        channel=conn,
        durable=True,
        queue_arguments=arguments,
    )
    retry_queue.declare()


def init_task_exchange(conn: Connection) -> None:
    logger.info("Initialising task exchange")
    task_exchange: Exchange = get_task_exchange(conn)
    task_exchange.declare()


def get_task_exchange(conn: Connection) -> Exchange:
    return Exchange(
        TASK_EXCHANGE_NAME, type=TASK_EXCHANGE_TYPE, channel=conn, durable=True
    )
