from typing import Optional

from environs import Env

env: Env = Env()

# Rabbit connection details
_rabbitmq_host: Optional[str] = env.str("RABBITMQ_HOST", default=None)
_rabbitmq_port: int = env.int("RABBITMQ_PORT", default=5672)
_rabbitmq_username: Optional[str] = env.str("RABBITMQ_USERNAME", default=None)
_rabbitmq_password: Optional[str] = env.str("RABBITMQ_PASSWORD", default=None)
RABBITMQ_CONNECTION_STRING: str = f"amqp://{_rabbitmq_username}:{_rabbitmq_password}@{_rabbitmq_host}:{_rabbitmq_port}//"
RABBITMQ_DISABLED: bool = env.bool("RABBITMQ_DISABLED", default=False)
RABBITMQ_COMPRESSION: Optional[str] = (
    env.str("RABBITMQ_COMPRESSION", default="bzip2") or None
)

# Initialisation flag
INITIALISED = False

if RABBITMQ_DISABLED is True:
    # Override connection string to prevent confusion.
    RABBITMQ_CONNECTION_STRING = "disabled"
else:
    # Ensure these env vars are set.
    env.str("RABBITMQ_HOST")
    env.str("RABBITMQ_USERNAME")
    env.str("RABBITMQ_PASSWORD")
