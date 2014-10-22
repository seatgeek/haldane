import gevent.monkey
gevent.monkey.patch_all()

import boto
import boto.ec2
import json
import lru

from flask import Blueprint
from flask import request
from flask import Response

from haldane.config import Config
from haldane.utils import set_retrieve
from haldane.utils import sorted_dict
from haldane.utils import sorted_json
from haldane.utils import to_bool


blueprint_http = Blueprint('blueprint_http', __name__)


@blueprint_http.app_errorhandler(404)
def page_not_found(e):
    return Response(
        json.dumps({'status': 'Not Found'}),
        mimetype='application/json',
        status=404
    )


@blueprint_http.route('/')
@blueprint_http.route('/_status')
def status():
    return Response(
        json.dumps({'status': 'ok'}),
        mimetype='application/json',
    )


@blueprint_http.route('/nodes/group')
@blueprint_http.route('/nodes/group/<region>')
def nodes_by_group(region=None):
    query = request.args.get('query')
    regions = get_regions(region)
    nodes = get_nodes(regions, query)

    groups = sort_by_group(nodes)

    data = {
        'meta': {
            'total': len(groups),
            'regions': regions,
        },
        'groups': groups
    }
    return Response(
        sorted_json(data),
        mimetype='application/json',
    )


@blueprint_http.route('/nodes')
@blueprint_http.route('/nodes/<region>')
def nodes(region=None):
    query = request.args.get('query')
    regions = get_regions(region)
    nodes = get_nodes(regions, query)

    data = {
        'meta': {
            'total': len(nodes),
            'regions': regions,
        },
        'nodes': nodes
    }
    return Response(
        sorted_json(data),
        mimetype='application/json',
    )


def get_regions(region=None):
    regions = [region]
    if region is None:
        regions = Config.AWS_REGIONS
    return regions


def get_nodes(regions, query=None):
    nodes = {}
    for region in regions:
        nodes.update(get_nodes_in_region(region))

    if query is not None:
        _nodes = {}
        for name, node in nodes.items():
            if query in name:
                _nodes[name] = node
        nodes = _nodes
    return nodes


def sort_by_group(nodes):
    groups = {
        'None': {}
    }
    for name, node in nodes.items():
        group = node.get('group', None)
        if group is None:
            groups['None'][name] = node
        else:
            if group not in groups:
                groups[group] = {}
            groups[group][name] = node

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
            'group': group
        })

    return sorted_dict(instances)
