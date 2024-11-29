import logging


class AttributeLogger:
    """
    A class that adds attributes as extra parameters to every log call.

    Attributes:
        logger (logging.Logger): The logger object to use for logging.

    Methods:
        debug: Logs a message with the DEBUG level.
        info: Logs a message with the INFO level.
        warning: Logs a message with the WARNING level.
        error: Logs a message with the ERROR level.
        fatal: Logs a message with the FATAL level.
        critical: Logs a message with the CRITICAL level.
        with_attributes: Returns a new AttributeLogger object with additional attributes.
    """

    logger: logging.Logger

    def __init__(self, logger: logging.Logger, **attr):
        self._logger = logger
        self._attributes = attr

    def _log(self, level, msg, *args, **kwargs):
        kwargs["extra"] = self._attributes
        kwargs["stacklevel"] = 2
        level(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(self._logger.debug, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(self._logger.info, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(self._logger.warning, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(self._logger.error, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self._log(self._logger.fatal, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(self._logger.critical, msg, *args, **kwargs)

    def with_attributes(self, **kwargs):
        new_attrs = self._attributes.copy()
        new_attrs.update(kwargs)
        return AttributeLogger(self._logger, **new_attrs)
