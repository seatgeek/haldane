import gevent.monkey
gevent.monkey.patch_all()  # noqa

import boto3
import botocore
import json
import time

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

from app.aws import format_elements
from app.aws import get_amis
from app.aws import get_instance_types
from app.aws import get_nodes
from app.aws import get_regions
from app.aws import get_status
from app.aws import limit_elements
from app.aws import sort_by_group
from app.basic_auth import requires_auth
from app.config import Config
from app.log import getLogger
from app.log import getRequestLogger
from app.log import log_request
from app.ssl_279 import _ssl
from app.utils import sorted_json

_ssl  # hack to avoid "Imported but not used" validation issue
blueprint_http = Blueprint('blueprint_http', __name__)
logger = getLogger('haldane')
request_logger = getRequestLogger()
aws_docs_domain = 'http://docs.aws.amazon.com'
error_link = '{0}/AWSEC2/latest/APIReference/errors-overview.html'.format(
    aws_docs_domain)


@blueprint_http.app_errorhandler(404)
def page_not_found(e):
    return Response(
        json.dumps({'status': 'Not Found'}),
        mimetype='application/json',
        status=404
    )


@blueprint_http.errorhandler(boto3.exceptions.Boto3Error)
def handle_boto3_response_error(error):
    logger.info('{0}'.format(error))
    response = jsonify({
        'type': error_link,
        'title': '{0} Error in EC2 Response'.format(error),
        'status': 500,
    })
    response.status_code = 500
    return response


@blueprint_http.errorhandler(botocore.exceptions.BotoCoreError)
def handle_botocore_response_error(error):
    logger.info('{0}'.format(vars(error)))
    response = jsonify({
        'type': error_link,
        'title': '{0} Error in EC2 Response'.format(error),
        'status': 500,
    })
    response.status_code = 500
    return response


@blueprint_http.errorhandler(LookupError)
def handle_lookup_error(error):
    logger.info('LookupError: {0}'.format(error.message))
    response = jsonify({
        'title': 'Invalid argument passed',
        'detail': error.message,
        'status': 400,
    })
    response.status_code = 400
    return response


@blueprint_http.after_request
def log_http_request(response):
    log_request(request, response, request_logger)
    return response


@blueprint_http.route('/')
@blueprint_http.route('/_status')
def status():
    return json_response({
        '_service': {
            '_settings': {
                'regions': Config.AWS_REGIONS,
                'cache': {
                    'expiration': Config.CACHE_EXPIRATION,
                    'size': Config.CACHE_SIZE
                }
            },
            'environment': 'dev' if Config.DEBUG else 'prod',
            'name': 'haldane'
        },
        'meta': {
            'status': 200
        },
        'ok': True
    })


@blueprint_http.route('/amis')
@requires_auth
def amis():
    time_start = time.time()
    query = request.args.get('query', request.args.get('q'))
    regions = get_regions(request.args.get('region'))
    amis = get_amis(request.args, regions, query)

    total_amis = len(amis)
    amis = limit_elements(amis, limit=request.args.get('limit'))
    total_not_hidden = len(amis)
    amis = format_elements(
        amis,
        fields=request.args.get('fields'),
        format=request.args.get('format'))
    total_hidden = total_not_hidden - len(amis)

    if request.args.get('format') == 'csv':
        return csv_response(amis)

    return json_response({
        'meta': {
            'took': time.time() - time_start,
            'total': total_amis,
            'hidden_nodes': total_hidden,
            'regions': regions,
            'per_page': len(amis)
        },
        'amis': amis,
    })


@blueprint_http.route('/instance-types')
@blueprint_http.route('/instance-types/<version>')
@requires_auth
def instance_types(version=None):
    time_start = time.time()
    instance_types, version = get_instance_types(version)

    total_instance_types = len(instance_types)

    return json_response({
        'meta': {
            'api_version': version,
            'took': time.time() - time_start,
            'total': total_instance_types,
            'per_page': len(instance_types)
        },
        'instance-types': instance_types,
    })


@blueprint_http.route('/nodes/group')
@blueprint_http.route('/nodes/group/<group>')
@requires_auth
def nodes_by_group(group=None):
    time_start = time.time()
    query = request.args.get('query', request.args.get('q'))
    regions = get_regions(request.args.get('region'))
    status = get_status(request.args.get('status'))
    nodes = get_nodes(request.args,
                      regions,
                      query,
                      status=status)
    groups = sort_by_group(nodes, group=group)

    total_hidden = 0
    _groups = {}
    for group, nodes in groups.items():
        total_nodes = len(nodes)
        _groups[group] = format_elements(
            nodes,
            fields=request.args.get('fields'),
            format=request.args.get('format', 'dict'))
        total_hidden += total_nodes - len(_groups[group])

    return json_response({
        'meta': {
            'took': time.time() - time_start,
            'total': len(groups),
            'hidden_nodes': total_hidden,
            'regions': regions,
            'per_page': len(groups)
        },
        'groups': _groups
    })


@blueprint_http.route('/nodes')
@blueprint_http.route('/nodes/<region>')
@requires_auth
def nodes(region=None):
    time_start = time.time()
    query = request.args.get('query', request.args.get('q'))
    regions = get_regions(request.args.get('region', region))
    status = get_status(request.args.get('status'))
    nodes = get_nodes(request.args,
                      regions,
                      query,
                      status=status)

    total_nodes = len(nodes)
    nodes = limit_elements(nodes, limit=request.args.get('limit'))
    total_not_hidden = len(nodes)
    nodes = format_elements(
        nodes,
        fields=request.args.get('fields'),
        format=request.args.get('format'))
    total_hidden = total_not_hidden - len(nodes)

    if request.args.get('format') == 'csv':
        return csv_response(nodes)

    return json_response({
        'meta': {
            'took': time.time() - time_start,
            'total': total_nodes,
            'hidden_nodes': total_hidden,
            'regions': regions,
            'per_page': len(nodes)
        },
        'nodes': nodes
    })


def json_response(data):
    return Response(
        sorted_json(data),
        mimetype='application/json',
    )

def csv_response(data):
    resp = []
    header = []
    fields = request.args.get('fields')
    for instance, data in data.items():
        header = data.keys()
        values = data.values()
        if fields:
            values = []
            for field in fields.split(','):
                values.append(str(data.get(field, '')))
        resp.append(','.join(values))

    if fields:
        header = [fields]
    else:
        header = [','.join(header)]

    return Response(
        "\n".join(header + resp),
        mimetype="text/csv"
    )
