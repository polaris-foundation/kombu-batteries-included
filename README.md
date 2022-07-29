# Kombu Batteries Included

This library extends the `kombu` base package, and includes:
- Configuration for connection to platform instances of RabbitMQ
- Initialisation/declaring of infrastructure such as exchanges and error/retry queues
- Utility functions for publishing messages

## Maintainers
The Polaris platform was created by Sensyne Health Ltd., and has now been made open-source. As a result, some of the
instructions, setup and configuration will no longer be relevant to third party contributors. For example, some of
the libraries used may not be publicly available, or docker images may not be accessible externally. In addition, 
CICD pipelines may no longer function.

For now, Sensyne Health Ltd. and its employees are the maintainers of this repository.

## Installation

Follow the usual setup guide for platform engineers then run `make install`

## Usage

To use this library in your app:

1) Set the required env vars:
```shell script
export RABBITMQ_HOST=localhost
export RABBITMQ_USERNAME=user
export RABBITMQ_PASSWORD=bitnami
```

2) Add an initialisation call when your app starts:
```python
import kombu_batteries_included

kombu_batteries_included.init()
``` 

3) Publish away!
```python
import kombu_batteries_included

payload = {"message_key": "message_value"}
kombu_batteries_included.publish_message(routing_key="dhos.12345", body=payload)
```

You can disable interaction with RabbitMQ for testing purposes by setting the env var `RABBITMQ_DISABLED` to `true`. When writing unit tests, you can also monkeypatch config.RABBITMQ_DISABLED for setting up individual tests.

Set the env var `RABBITMQ_COMPRESSION` to control message compression. By default all messages are compressed using `bzip2`, set the env var to `zip` for zip compression or set it to an empty string to disable compression.
