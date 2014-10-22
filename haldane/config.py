import os
from haldane.utils import to_bool


class Config(object):
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_REGIONS = os.getenv('AWS_REGIONS', 'us-east-1').split(',')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', 180))
    CACHE_SIZE = int(os.getenv('CACHE_SIZE', 1024))
    DEBUG = to_bool(os.getenv('DEBUG', 0))
    PORT = int(os.getenv('PORT', 5000))
    SUPPRESS_SENTRY = to_bool(os.getenv('SUPPRESS_SENTRY', 0))
