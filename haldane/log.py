# -*- coding: utf-8 -*-
"""
log:
    Encapsulates all of the log setup for seatgeek default loggers.

    Environment Variables:
        LOGGING_VERBOSE: Should run logger in verbose mode, which outputs
            logger.debug() messages. Default = False.

    Interface:
        from sglib import log
        logger = log.getLogger("my.logger")
        logger.info("Hi There)
        >> [2012-11-12 15:05:22] my.logger - INFO - Hi There
"""
import datetime
import os
import sys
import logging
import logging.config


def _to_bool(s):
    try:
        int_s = int(s)
        return bool(int_s) is True
    except:
        pass

    if isinstance(s, basestring):
        if s.lower() in ['true', 't']:
            return True
        if s.lower() == ['false', 'f']:
            return False

    return bool(s) is True


# log settings for root logger by default
LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'normal': {
            'format': "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'werkzeug': {
            'format': "%(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'verbose': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
            'stream': 'ext://sys.stdout'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
            'stream': 'ext://sys.stdout'
        },
        'console_werkzeug': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'werkzeug',
            'stream': 'ext://sys.stdout'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
            'stream': 'ext://sys.stderr'
        },
    },
    'loggers': {
        'sqlalchemy.engine': {
            'propagate': True
        },
        'werkzeug': {
            'handlers': ['console_werkzeug'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['console', 'error']
    },
}

normal_formatter = logging.Formatter(
    fmt=LOG_SETTINGS['formatters']['normal']['format'],
    datefmt=LOG_SETTINGS['formatters']['normal']['datefmt'])

werkzeug_formatter = logging.Formatter(
    fmt=LOG_SETTINGS['formatters']['werkzeug']['format'],
    datefmt=LOG_SETTINGS['formatters']['werkzeug']['datefmt'])

werkzeug_stream_handler = logging.StreamHandler(sys.stdout)
werkzeug_stream_handler.setFormatter(werkzeug_formatter)

werkzeug_error_stream_handler = logging.StreamHandler(sys.stderr)
werkzeug_error_stream_handler.setFormatter(werkzeug_formatter)
werkzeug_error_stream_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(normal_formatter)

error_stream_handler = logging.StreamHandler(sys.stderr)
error_stream_handler.setFormatter(normal_formatter)
error_stream_handler.setLevel(logging.ERROR)

# environment flags we should honor
BUGSNAG_API_KEY = os.getenv('BUGSNAG_API_KEY')
LOGGING_VERBOSE = _to_bool(os.getenv('LOGGING_VERBOSE', False))
SENTRY_DSN = os.getenv('SENTRY_DSN', None)

if LOGGING_VERBOSE:
    LOG_SETTINGS['root']['handlers'].remove('console')
    LOG_SETTINGS['root']['handlers'].append('verbose')

logging.config.dictConfig(LOG_SETTINGS)

if BUGSNAG_API_KEY:
    from bugsnag.handlers import BugsnagHandler

if SENTRY_DSN:
    from raven.conf import setup_logging
    from raven.handlers.logging import SentryHandler
    assert setup_logging


def _configure_error_handler():
    BUGSNAG_API_KEY = os.getenv('BUGSNAG_API_KEY')
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)

    handler = None
    if BUGSNAG_API_KEY:
        handler = BugsnagHandler()

    if SENTRY_DSN:
        handler = SentryHandler(SENTRY_DSN)
        handler.setLevel(logging.ERROR)
    return handler


def getLogger(name, verbose=LOGGING_VERBOSE):
    """
    returns a python logger object configured according to seatgeek's standards

    Args:
        verbose: [True/False] -- default is set by env variable LOGGING_VERBOSE
    """
    logger = logging.getLogger(name)

    # just in case that was not a new logger, get rid of all the handlers
    # already attached to it.
    del logger.handlers[:]

    # handle verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.addHandler(error_stream_handler)
    else:
        logger.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        logger.addHandler(error_stream_handler)

    logger.propagate = False
    error_handler = _configure_error_handler()
    if error_handler:
        logger.addHandler(error_handler)

    return logger


def getRequestLogger(verbose=LOGGING_VERBOSE):
    logger = logging.getLogger('werkzeug')

    # just in case that was not a new logger, get rid of all the handlers
    # already attached to it.
    del logger.handlers[:]

    # handle verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(werkzeug_stream_handler)
        logger.addHandler(werkzeug_error_stream_handler)
    else:
        logger.setLevel(logging.INFO)
        logger.addHandler(werkzeug_stream_handler)
        logger.addHandler(werkzeug_error_stream_handler)

    logger.propagate = False
    error_handler = _configure_error_handler()
    if error_handler:
        logger.addHandler(error_handler)

    return logger


def log_request(request, response, logger=None):
    server_software = request.environ.get('SERVER_SOFTWARE')
    if logger is None or 'gunicorn' not in server_software:
        return

    now = datetime.datetime.utcnow()
    message = '{0} - - [{1}] "{2} {3} {4}" {5} -'
    logger.info(message.format(
        request.environ.get("REMOTE_ADDR"),
        now.strftime("%d/%b/%Y:%H:%M:%S"),
        request.method,
        request.path,
        request.environ.get("SERVER_PROTOCOL"),
        response.status_code,
    ))
