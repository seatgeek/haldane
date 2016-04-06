import functools

from flask import request
from flask import Response

from haldane.config import Config
from haldane.log import getLogger


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    logger = getLogger('haldane')
    provided_ips = request.access_route

    logger.info('Provided IPs: {0}'.format(provided_ips))
    logger.info('Allowed IPs: {0}'.format(Config.ALLOWED_IPS))
    if len(provided_ips) > 0 and provided_ips[0] in Config.ALLOWED_IPS:
        return True

    authentications = Config.BASIC_AUTH.split(',')
    authentication = '{0}:{1}'.format(username, password)

    return authentication in authentications


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not Config.BASIC_AUTH:
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
