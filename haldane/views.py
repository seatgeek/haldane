import gevent.monkey
gevent.monkey.patch_all()

import boto
import boto.ec2
import json
import lru
import time

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

from haldane.basic_auth import requires_auth
from haldane.config import Config
from haldane.log import getLogger
from haldane.log import getRequestLogger
from haldane.log import log_request
from haldane.ssl_279 import _ssl
from haldane.utils import set_retrieve
from haldane.utils import sorted_dict
from haldane.utils import sorted_json
from haldane.utils import to_bool

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


@blueprint_http.errorhandler(boto.exception.EC2ResponseError)
def handle_ec2_response_error(error):
    logger.info('{0}: {1}'.format(error.error_code, error.error_message))
    response = jsonify({
        'type': error_link,
        'title': '{0} Error in EC2 Respone'.format(error.error_code),
        'detail': error.error_message,
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
    return json_response({'status': 'ok'})


@blueprint_http.route('/nodes/group')
@blueprint_http.route('/nodes/group/<group>')
@requires_auth
def nodes_by_group(group=None):
    time_start = time.time()
    query = request.args.get('query', request.args.get('q'))
    regions = get_regions(request.args.get('region'))
    status = get_status(request.args.get('status'))
    nodes = get_nodes(regions, query, status=status)
    groups = sort_by_group(nodes, group=group)

    _groups = {}
    for group, nodes in groups.items():
        _groups[group] = format_nodes(nodes, format=request.args.get('format'))

    return json_response({
        'meta': {
            'took': time.time() - time_start,
            'total': len(groups),
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
    regions = get_regions(region)
    status = get_status(request.args.get('status'))
    nodes = get_nodes(regions, query, status=status)
    total_nodes = len(nodes)
    nodes = limit_nodes(nodes, limit=request.args.get('limit'))
    nodes = format_nodes(nodes, format=request.args.get('format'))

    return json_response({
        'meta': {
            'took': time.time() - time_start,
            'total': total_nodes,
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


def get_status(status=None):
    if status is None:
        return None
    valid_states = [
        'pending',
        'running',
        'shutting-down',
        'terminated',
        'stopping',
        'stopped',
    ]
    if status not in valid_states:
        raise LookupError('Invalid status querystring argument passed.')

    return status


def get_regions(region=None):
    regions = []
    if region is None:
        regions = Config.AWS_REGIONS
    else:
        if region not in Config.AWS_REGIONS:
            raise LookupError('Invalid region querystring argument passed')
        regions = [region]
    return regions


def get_nodes(regions, query=None, status=None):
    nodes = {}
    for region in regions:
        nodes.update(get_nodes_in_region(region))

    if status is not None:
        _nodes = {}
        for name, node in nodes.items():
            if node.get('status') == status:
                _nodes[name] = node
        nodes = _nodes

    if query is not None:
        _nodes = {}
        for name, node in nodes.items():
            if query in name:
                _nodes[name] = node
        nodes = _nodes

    group = request.args.get('group', None)
    if group is not None:
        _nodes = {}
        for name, node in nodes.items():
            _group = node.get('group', '')
            if not _group:
                continue

            if _group == group:
                _nodes[name] = node
        nodes = _nodes

    tag_filters = get_tag_filters(request.args)
    for key, value in tag_filters.items():
        _nodes = {}
        for name, node in nodes.items():
            tag = node.get('tags', {}).get(key)
            if not tag:
                continue

            if value in tag:
                _nodes[name] = node
        nodes = _nodes

    return nodes


def get_tag_filters(args):
    tags = {}
    for key, value in args.items():
        if key.startswith('tags.'):
            tags[key[5:]] = value
    return tags


def limit_nodes(nodes, limit=None):
    if limit is None:
        return nodes

    count = 0
    limit = int(limit)
    _nodes = {}
    for name, node in nodes.items():
        if count == limit:
            break

        count += 1
        _nodes[name] = node
    return _nodes


def format_nodes(nodes, format=None):
    if format == 'list':
        return nodes.values()

    return nodes


def sort_by_group(nodes, group=None):
    groups = {
        'None': {}
    }
    for name, node in nodes.items():
        if node.get('group') is None:
            groups['None'][name] = node
        else:
            if node.get('group') not in groups:
                groups[node.get('group')] = {}
            groups[node.get('group')][name] = node

    if group is not None:
        if group in groups:
            groups = {group: groups[group]}
        else:
            groups = {}

    return groups


@lru.lru_cache_function(
    max_size=Config.CACHE_SIZE,
    expiration=Config.CACHE_EXPIRATION)
def get_nodes_in_region(region):
    conn = boto.ec2.connect_to_region(
        region,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )

    if conn is None:
        return {}

    instances = {}
    reservations = conn.get_all_reservations()
    instances_for_region = [i for r in reservations for i in r.instances]
    for instance in instances_for_region:
        instance_data = instance.__dict__
        name = set_retrieve(instance_data, 'tags.Name')
        ip_address = set_retrieve(instance_data, 'ip_address')
        pip_address = set_retrieve(instance_data, 'private_ip_address')
        instance_id = set_retrieve(instance_data, 'id')

        if ip_address is None:
            ip_address = ''
        if pip_address is None:
            pip_address = ''
        if instance_id is None:
            instance_id = ''

        tags = set_retrieve(instance_data, 'tags')
        if not tags:
            tags = {}

        group = tags.get('aws:autoscaling:groupName', '')
        bootstrapped = to_bool(tags.get('bootstrapped', ''))

        if not name:
            name = group + '-' + instance_id

        if group == '':
            group = None

        instances[name.replace('_', '-').strip()] = sorted_dict({
            'name': name.replace('_', '-').strip(),
            'ip_address': ip_address,
            'private_ip_address': pip_address,
            'status': instance.state,
            'region': region,
            'instance_type': instance.instance_type,
            'id': instance_id,
            'bootstrapped': bootstrapped,
            'group': group,
            'tags': tags,
        })

    return sorted_dict(instances)
