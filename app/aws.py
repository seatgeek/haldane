import gevent.monkey
gevent.monkey.patch_all()  # noqa

import boto3
import json
import lru

from botocore import BOTOCORE_ROOT
from inflection import underscore

from app.config import Config
from app.filters import filter_elements
from app.log import getLogger
from app.utils import sorted_dict
from app.utils import to_bool


logger = getLogger('haldane')


def get_amis(request_args, regions, query=None):
    amis = []
    for region in regions:
        ec2_resource = boto3.resource('ec2', region_name=region)
        amis.extend(get_amis_in_region(ec2_resource, region))

    return filter_elements(amis, request_args, query=query)


def get_nodes(request_args, regions, query=None, status=None):
    nodes = []
    for region in regions:
        nodes.extend(get_nodes_in_region(region))

    return filter_elements(nodes, request_args, query=query, status=status)


def get_regions(region=None):
    regions = []
    if region is None:
        regions = Config.AWS_REGIONS
    else:
        if region not in Config.AWS_REGIONS:
            raise LookupError('Invalid region querystring argument passed')
        regions = [region]
    return regions


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
def get_instance_types(version=None):
    if version is None:
        version = Config.AWS_API_VERSION
    filename = '{0}/data/ec2/{1}/service-2.json'.format(BOTOCORE_ROOT, version)
    with open(filename) as f:
        data = json.loads(f.read())
        return data['shapes']['InstanceType']['enum'], version
    return [], version


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
        if not tags:
            tags = []
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
