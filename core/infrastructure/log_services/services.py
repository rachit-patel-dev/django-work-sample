import datetime
import logging

import json_log_formatter
import ujson

logging.addLevelName(logging.CRITICAL, "FATAL")


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    """
    A custom JSON formatter class that extends the
    JSONFormatter class from the json_log_formatter module.

    Attributes:
        json_lib (module): The JSON library to use for encoding the log records.
        Default is ujson.

    Methods:
        json_record(message, extra, record): Formats the log record into a JSON object.
    """

    json_lib = ujson

    def json_record(self, message, extra, record) -> dict:
        """
        Formats the log record into a JSON object.

        Parameters:
            message (str): The log message.
            extra (dict): Additional log record attributes.
            record (logging.LogRecord): The log record object.

        Returns:
            dict: The formatted log record as a JSON object.
        """
        extra["level"] = record.__dict__["levelname"]
        extra["msg"] = message
        extra["logger"] = record.__dict__["name"]
        extra["func"] = record.__dict__["funcName"]
        extra["line"] = record.__dict__["lineno"]
        extra["time"] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        request = extra.pop("request", None)
        if request:
            extra["x_forward_for"] = request.META.get("X-FORWARD-FOR")
        return extra
