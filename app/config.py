import os
from app.utils import to_bool


class Config(object):
    ALLOWED_IPS = filter(None, os.getenv('ALLOWED_IPS', '').split(','))
    ALTERNATIVE_AUTOSCALE_TAG_NAME = os.getenv('ALTERNATIVE_AUTOSCALE_TAG_NAME', None)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_API_VERSION = os.getenv('AWS_API_VERSION', '2016-09-15')
    AWS_REGIONS = filter(None, os.getenv('AWS_REGIONS', 'us-east-1').split(','))
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BASIC_AUTH = os.getenv('BASIC_AUTH')
    BOOLEAN_AWS_TAG_ATTRIBUTES = filter(None, os.getenv('BOOLEAN_AWS_TAG_ATTRIBUTES', '').split(','))
    BUGSNAG_API_KEY = os.getenv('BUGSNAG_API_KEY')
    CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', 180))
    CACHE_SIZE = int(os.getenv('CACHE_SIZE', 1024))
    DEBUG = to_bool(os.getenv('DEBUG', 0))
    LISTEN_INTERFACE = os.getenv('LISTEN_INTERFACE', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    SENTRY_DSN = os.getenv('SENTRY_DSN')
