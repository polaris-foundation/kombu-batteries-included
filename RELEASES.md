# 1.1.4
- Move hosting to public pypi

# 1.1.3
- Update dependencies

# 1.1.2
- Update dependencies including kombu 5.*
- Allow publishing messages with existing headers

# 1.1.1
- Published messages now set correlation_id and timestamp

# 1.1.0
- Compress rabbit messages

# 1.0.3
- Fixed datetime conversion to use ISO8601 format

# 1.0.2
- Changed publish to enforce library initialisation
- Allowed publishing of message with a list body

# 1.0.1
- Changed publish to handle datetimes in message body
- Changed config to not require RABBITMQ env vars if RABBITMQ_DISABLED is set

# 1.0.0
- Initial release
