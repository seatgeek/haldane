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

from app.basic_auth import requires_auth
from app.config import Config
from app.log import getLogger
from app.log import getRequestLogger
from app.log import log_request
from app.ssl_279 import _ssl
from app.utils import set_retrieve
from app.utils import sorted_dict
from app.utils import sorted_json
from app.utils import to_bool

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
    amis = get_amis(regions, query)

    total_amis = len(amis)
    amis = limit_elements(amis, limit=request.args.get('limit'))
    total_not_hidden = len(amis)
    amis = format_elements(amis,
        fields=request.args.get('fields'),
        format=request.args.get('format'))
    total_hidden = total_not_hidden - len(amis)

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

def get_amis(regions, query=None):
    amis = []
    for region in regions:
        amis.extend(get_amis_in_region(region))

    return filter_elements(amis, query=query)


@blueprint_http.route('/nodes/group')
@blueprint_http.route('/nodes/group/<group>')
@requires_auth
def nodes_by_group(group=None):
    time_start = time.time()
    query = request.args.get('query', request.args.get('q'))
    regions = get_regions(request.args.get('region'))
    status = get_status(request.args.get('status'))
    nodes = get_nodes(regions,
                      query,
                      status=status)
    groups = sort_by_group(nodes, group=group)

    total_hidden = 0
    _groups = {}
    for group, nodes in groups.items():
        total_nodes = len(nodes)
        _groups[group] = format_elements(nodes,
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
    nodes = get_nodes(regions,
                      query,
                      status=status)

    total_nodes = len(nodes)
    nodes = limit_elements(nodes, limit=request.args.get('limit'))
    total_not_hidden = len(nodes)
    nodes = format_elements(nodes,
        fields=request.args.get('fields'),
        format=request.args.get('format'))
    total_hidden = total_not_hidden - len(nodes)

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


def filter_elements(elements, query=None, status=None):
    elements = filter_by_args(elements, request)
    elements = filter_by_tags(elements, request)

    return elements

def filter_by_args(elements, request):
    exact_filters, list_filters, substring_filters, starts_with_filters, ends_with_filters = get_filters(
        request.args)

    bool_search_keys = [
        'elastic_ip',
    ]

    for key, value in exact_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key, '')
            if not attribute and value:
                continue

            if key in bool_search_keys:
                attribute = to_bool(attribute)

            if value == attribute:
                _elements.append(element)
        elements = _elements
    for key, value in list_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if value in attribute.split(','):
                _elements.append(element)
        elements = _elements
    for key, value in substring_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if value in attribute:
                _elements.append(element)
        elements = _elements
    for key, value in starts_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if attribute.startswith(value):
                _elements.append(element)
        elements = _elements
    for key, value in ends_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if attribute.endswith(value):
                _elements.append(element)
        elements = _elements

    return elements


def filter_by_tags(elements, request):
    exact_filters, list_filters, substring_filters, starts_with_filters, ends_with_filters = get_tag_filters(
        request.args)

    for key, value in exact_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute and value:
                continue

            if value == attribute:
                _elements.append(element)
        elements = _elements
    for key, value in list_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if value in attribute.split(','):
                _elements.append(element)
        elements = _elements
    for key, value in substring_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if value in attribute:
                _elements.append(element)
        elements = _elements
    for key, value in starts_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if attribute.startswith(value):
                _elements.append(element)
        elements = _elements
    for key, value in ends_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if attribute.endswith(value):
                _elements.append(element)
        elements = _elements

    return elements


def format_elements(elements, fields=None, format=None):
    if fields:
        fields = fields.split(',')
        _elements = []
        for element in elements:
            _element = {}
            if format == 'dict':
                _element['name'] = element['name']
            for field in fields:
                if field in element:
                    _element[field] = element.get(field)
            _elements.append(_element)
        elements = _elements
    if format == 'list':
        return elements

    _elements = {}
    for element in elements:
        name = element['name']
        if name in _elements:
            existing = _elements[name]
            logger.warning('duplicate name collission: {0}'.format(
                name))
            logger.warning('existing running instance id: {0}'.format(
                existing['id']))
            logger.warning('new instance id: {0}'.format(element['id']))
            if element.get('status', '') == 'running':
                logger.warning('hiding existing resource {0} in state {1}'.format(  # noqa
                    existing['id'],
                    existing.get('status', '')))
            else:
                logger.warning('hiding new resource {0} in state {1}'.format(
                    element['id'],
                    element.get('status', '')))
                continue
        _elements[name] = element

    return sorted_dict(_elements)


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
    nodes = []
    for region in regions:
        nodes.extend(get_nodes_in_region(region))

    return filter_elements(nodes, query=query, status=status)


def get_filters(args):
    exact = {}
    in_list = {}
    substring = {}
    ends_with = {}
    starts_with = {}
    search_keys = [
        'availability_zone',
        'elastic_ip',
        'group',
        'id',
        'image_id',
        'image_name',
        'instance_type',
        'instance_class',
        'name',
        'status',
    ]
    bool_search_keys = [
        'elastic_ip',
    ]

    query = request.args.get('query', request.args.get('q'))
    if query:
        substring['name'] = query

    for key, value in args.items():
        if key in bool_search_keys:
            value = to_bool(value)

        if key.startswith('starts-with.') and key[12:] in search_keys:
            starts_with[key[12:]] = value
        elif key.startswith('ends-with.') and key[10:] in search_keys:
            ends_with[key[10:]] = value
        elif key.startswith('substring.') and key[10:] in search_keys:
            substring[key[10:]] = value
        elif key.startswith('in-list.') and key[8:] in search_keys:
            in_list[key[8:]] = value
        elif key.startswith('exact.') and key[6:] in search_keys:
            exact[key[6:]] = value
        elif key in search_keys:
            exact[key] = value

    return exact, in_list, substring, starts_with, ends_with


def get_tag_filters(args):
    exact = {}
    in_list = {}
    substring = {}
    ends_with = {}
    starts_with = {}
    for key, value in args.items():
        if key.startswith('tags.starts-with.'):
            starts_with[key[17:]] = value
        elif key.startswith('tags.ends-with.'):
            ends_with[key[15:]] = value
        elif key.startswith('tags.substring.'):
            substring[key[15:]] = value
        elif key.startswith('tags.in-list.'):
            in_list[key[13:]] = value
        elif key.startswith('tags.exact.'):
            exact[key[11:]] = value
        elif key.startswith('tags.'):
            exact[key[5:]] = value
    return exact, in_list, substring, starts_with, ends_with


def limit_elements(elements, limit=None):
    if limit is None:
        return elements

    count = 0
    limit = int(limit)
    _elements = []
    for element in elements:
        if count == limit:
            break

        count += 1
        _elements.append(element)
    return _elements


def sort_by_group(nodes, group=None):
    groups = {
        'None': []
    }
    for node in nodes:
        if node.get('group') is None:
            groups['None'].append(node)
        else:
            if node.get('group') not in groups:
                groups[node.get('group')] = []
            groups[node.get('group')].append(node)

    if group is not None:
        if group in groups:
            groups = {group: groups[group]}
        else:
            groups = {}

    return groups


@lru.lru_cache_function(
    max_size=Config.CACHE_SIZE,
    expiration=Config.CACHE_EXPIRATION)
def get_amis_in_region(region):
    conn = boto.ec2.connect_to_region(
        region,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )

    if conn is None:
        return {}

    images = conn.get_all_images(owners=['self'])
    amis = []
    for image in images:
        ami = {
            'architecture': image.architecture,
            'billing_products': image.billing_products,
            'creationDate': image.creationDate,
            'description': image.description,
            'hypervisor': image.hypervisor,
            'id': image.id,
            'instance_lifecycle': image.instance_lifecycle,
            'is_public': image.is_public,
            'item': image.item,
            'kernel_id': image.kernel_id,
            'location': image.location,
            'name': image.name,
            'ownerId': image.ownerId,
            'owner_alias': image.owner_alias,
            'owner_id': image.owner_id,
            'platform': image.platform,
            'product_codes': image.product_codes,
            'ramdisk_id': image.ramdisk_id,
            'region': image.region.name,
            'root_device_name': image.root_device_name,
            'root_device_type': image.root_device_type,
            'sriov_net_support': image.sriov_net_support,
            'state': image.state,
            'tags': image.tags,
            'type': image.type,
            'virtualization_type': image.virtualization_type,
        }
        block_device_mapping = {}
        for mount, block_device in image.block_device_mapping.items():
            block_device_mapping[mount] = vars(block_device)
            del block_device_mapping[mount]['connection']
        ami['block_device_mapping'] = block_device_mapping
        amis.append(ami)
    return amis


@lru.lru_cache_function(
    max_size=Config.CACHE_SIZE,
    expiration=Config.CACHE_EXPIRATION)
def get_elastic_ips(conn, region):
    return [address.public_ip for address in conn.get_all_addresses()]


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

    elastic_ips = get_elastic_ips(conn, region)
    images = get_amis_in_region(region)

    instances = []
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

        default_group_name = None
        if Config.ALTERNATIVE_AUTOSCALE_TAG_NAME:
            default_group_name = tags.get(Config.ALTERNATIVE_AUTOSCALE_TAG_NAME, '')
        group = tags.get('aws:autoscaling:groupName', default_group_name)

        if group == '' or group is None:
            group = None
            if not name:
                name = instance_id
        elif not name:
            name = group + '-' + instance_id

        instance_name = name.replace('_', '-').strip()

        image_name = [image['name'] for image in images if image['id'] == instance.image_id]
        if len(image_name) == 1:
            image_name = image_name[0]
        else:
            image_name = ''

        data = {
            'availability_zone': instance.placement,
            'group': group,
            'elastic_ip': ip_address in elastic_ips,
            'id': instance_id,
            'image_id': instance.image_id,
            'image_name': image_name,
            'instance_type': instance.instance_type,
            'instance_class': instance.instance_type.split('.')[0],
            'ip_address': ip_address,
            'launch_time': instance.launch_time,
            'name': instance_name,
            'private_ip_address': pip_address,
            'region': region,
            'status': instance.state,
            'tags': tags,
            'vpc_id': instance.vpc_id,
        }

        for key in Config.BOOLEAN_AWS_TAG_ATTRIBUTES:
            data[key] = to_bool(tags.get(key, ''))

        instances.append(sorted_dict(data))

    return instances
