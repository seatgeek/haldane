import gevent.monkey
gevent.monkey.patch_all()  # noqa

import boto3
import botocore
import json
import lru
import time

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

from inflection import underscore

from app.basic_auth import requires_auth
from app.config import Config
from app.filters import filter_elements
from app.log import getLogger
from app.log import getRequestLogger
from app.log import log_request
from app.ssl_279 import _ssl
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
    amis = get_amis(regions, query)

    total_amis = len(amis)
    amis = limit_elements(amis, limit=request.args.get('limit'))
    total_not_hidden = len(amis)
    amis = format_elements(
        amis,
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
        ec2_resource = boto3.resource('ec2', region_name=region)
        amis.extend(get_amis_in_region(ec2_resource, region))

    return filter_elements(amis, request.args, query=query)


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
    nodes = get_nodes(regions,
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


def format_elements(elements, fields=None, format=None):
    if fields:
        fields = fields.split(',')
        _elements = []
        for element in elements:
            _element = {}
            if format != 'list':
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
            logger.warning('duplicate name collision: {0}'.format(
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

    return filter_elements(nodes, request.args, query=query, status=status)


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
def get_amis_in_region(resource, region):
    amis = []
    for image in resource.images.filter(Owners=['self']).all():
        ami = {
            'architecture': image.architecture,
            'creation_date': image.creation_date,
            'description': image.description,
            'hypervisor': image.hypervisor,
            'id': image.image_id,
            'is_public': image.public,
            'kernel_id': image.kernel_id,
            'location': image.image_location,
            'name': image.name,
            'owner_alias': image.image_owner_alias,
            'owner_id': image.owner_id,
            'platform': image.platform,
            'product_codes': image.product_codes,
            'ramdisk_id': image.ramdisk_id,
            'region': region,
            'root_device_name': image.root_device_name,
            'root_device_type': image.root_device_type,
            'sriov_net_support': image.sriov_net_support,
            'state': image.state,
            'type': image.image_type,
            'virtualization_type': image.virtualization_type,
        }

        block_device_fields = [
            'attach_time',
            'delete_on_termination',
            'ebs',
            'encrypted',
            'ephemeral_name',
            'iops',
            'no_device',
            'snapshot_id',
            'status',
            'volume_id',
            'volume_size',
            'volume_type',
        ]

        block_device_mapping = {}
        for block_device in image.block_device_mappings:
            device_name = block_device['DeviceName']
            data = block_device.get('Ebs', {})
            data['ephemeral_name'] = block_device.get('VirtualName')
            data['no_device'] = block_device.get('NoDevice')
            data = dict((underscore(k), v) for k, v in data.iteritems())
            for field in block_device_fields:
                data[field] = data.get(field)
            block_device_mapping[device_name] = data

        tags = image.tags
        if not tags:
            tags = []

        ami['block_device_mapping'] = block_device_mapping
        ami['tags'] = dict((tag['Key'], tag['Value']) for tag in tags)
        amis.append(ami)
    return amis


@lru.lru_cache_function(
    max_size=Config.CACHE_SIZE,
    expiration=Config.CACHE_EXPIRATION)
def get_elastic_ips(ec2_resource):
    classic_addresses = ec2_resource.classic_addresses.all()
    return [address.public_ip for address in classic_addresses]


@lru.lru_cache_function(
    max_size=Config.CACHE_SIZE,
    expiration=Config.CACHE_EXPIRATION)
def get_nodes_in_region(region):
    ec2_resource = boto3.resource('ec2', region_name=region)
    elastic_ips = get_elastic_ips(ec2_resource)
    images = get_amis_in_region(ec2_resource, region)

    instances = []
    instances_for_region = ec2_resource.instances.all()
    for instance in instances_for_region:
        ip_address = instance.public_ip_address
        pip_address = instance.private_ip_address
        instance_id = instance.instance_id

        if ip_address is None:
            ip_address = ''
        if pip_address is None:
            pip_address = ''
        if instance_id is None:
            instance_id = ''

        tags = instance.tags
        tags = dict((tag['Key'], tag['Value']) for tag in tags)
        for tag, value in tags.items():
            if value.lower() in ['true', 'false']:
                tags[tag] = to_bool(value)
            if value.lower() in ['none', 'nil', 'null']:
                tags[tag] = None
        name = tags.get('Name')

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

        instance_profile_id = None
        instance_profile_name = None
        if instance.iam_instance_profile:
            instance_profile_id = instance.iam_instance_profile['Id']
            instance_profile_name = instance.iam_instance_profile['Arn'].split('/', 1)[1]

        data = {
            'availability_zone': instance.placement['AvailabilityZone'],
            'group': group,
            'elastic_ip': ip_address in elastic_ips,
            'id': instance_id,
            'image_id': instance.image_id,
            'image_name': image_name,
            'instance_type': instance.instance_type,
            'instance_class': instance.instance_type.split('.')[0],
            'ip_address': ip_address,
            'instance_profile_id': instance_profile_id,
            'instance_profile_name': instance_profile_name,
            'launch_time': instance.launch_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'name': instance_name,
            'private_ip_address': pip_address,
            'region': region,
            'status': instance.state['Name'],
            'tags': tags,
            'vpc_id': instance.vpc_id,
        }

        for key in Config.BOOLEAN_AWS_TAG_ATTRIBUTES:
            data[key] = to_bool(tags.get(key, ''))

        instances.append(sorted_dict(data))

    return instances
