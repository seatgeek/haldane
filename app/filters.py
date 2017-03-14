from app.config import Config
from app.utils import to_bool


def filter_elements(elements, request_args, query=None, status=None):
    request_args = request_args.to_dict()
    if query:
        request_args['substring.name'] = query
    elements = filter_by_args(elements, request_args)
    elements = filter_by_tags(elements, request_args)

    return elements


def filter_by_args(elements, args):
    valid_search_keys = [
        # common
        'availability_zone',
        'id',
        'name',
        'region'
        'status',

        #  ec2
        'elastic_ip',
        'group',
        'image_id',
        'image_name',
        'instance_type',
        'instance_class',
        'instance_profile_id',
        'instance_profile_name',
        'ip_address',
        'private_ip_address',
        'vpc_id',

        # rds
        'allocated_storage',
        'auto_minor_version_upgrade',
        'backup_retention_period',
        'ca_certificate_identifier',
        'copy_tags_to_snapshot',
        'db_instance_arn',
        'db_instance_class',
        'db_instance_port',
        'db_instance_status',
        'db_name',
        'dbi_resource_id',
        'engine',
        'engine_version',
        'enhanced_monitoring_resource_arn',
        'license_model',
        'master_username',
        'monitoring_interval',
        'monitoring_role_arn',
        'multi_az',
        'preferred_backup_window',
        'preferred_maintenance_window',
        'publicly_accessible',
        'secondary_availability_zone',
        'storage_encrypted',
        'storage_type',
    ] + Config.BOOLEAN_AWS_TAG_ATTRIBUTES
    bool_search_keys = [
        'elastic_ip',
    ] + Config.BOOLEAN_AWS_TAG_ATTRIBUTES
    not_starts_with_filters, args = get_filter(args, 'not-starts-with', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    not_ends_with_filters, args = get_filter(args, 'not-ends-with', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    not_substring_filters, args = get_filter(args, 'not-substring', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    not_in_list_filters, args = get_filter(args, 'not-in-list', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    starts_with_filters, args = get_filter(args, 'starts-with', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    ends_with_filters, args = get_filter(args, 'ends-with', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    substring_filters, args = get_filter(args, 'substring', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    is_false_filters, args = get_filter(args, 'is-false', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    is_true_filters, args = get_filter(args, 'is-true', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    is_null_filters, args = get_filter(args, 'is-null', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    in_list_filters, args = get_filter(args, 'in-list', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)
    exact_filters, args = get_filter(args, 'exact', valid_search_keys=valid_search_keys, bool_search_keys=bool_search_keys)

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
    for key, value in is_null_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key, '')
            if attribute is None:
                _elements.append(element)
        elements = _elements
    for key, value in is_true_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key, None)
            if attribute is True:
                _elements.append(element)
        elements = _elements
    for key, value in is_false_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key, None)
            if attribute is False:
                _elements.append(element)
        elements = _elements
    for key, value in in_list_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if attribute in value.split(','):
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

    for key, value in not_in_list_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if attribute not in value.split(','):
                _elements.append(element)
        elements = _elements
    for key, value in not_substring_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key, None)
            if attribute is None:
                continue

            if value not in attribute:
                _elements.append(element)
        elements = _elements
    for key, value in not_starts_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if not attribute.startswith(value):
                _elements.append(element)
        elements = _elements
    for key, value in not_ends_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get(key)
            if not attribute:
                continue

            if not attribute.endswith(value):
                _elements.append(element)
        elements = _elements

    return elements


def filter_by_tags(elements, args):
    not_starts_with_filters, args = get_filter(args, 'tags.not-starts-with')
    not_ends_with_filters, args = get_filter(args, 'tags.not-ends-with')
    not_substring_filters, args = get_filter(args, 'tags.not-substring')
    not_in_list_filters, args = get_filter(args, 'tags.not-in-list')
    starts_with_filters, args = get_filter(args, 'tags.starts-with')
    ends_with_filters, args = get_filter(args, 'tags.ends-with')
    substring_filters, args = get_filter(args, 'tags.substring')
    is_false_filters, args = get_filter(args, 'tags.is-false')
    is_true_filters, args = get_filter(args, 'tags.is-true')
    is_null_filters, args = get_filter(args, 'tags.is-null')
    in_list_filters, args = get_filter(args, 'tags.in-list')
    exact_filters, args = get_filter(args, 'tags.exact')

    for key, value in exact_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute and value:
                continue

            if value == attribute:
                _elements.append(element)
        elements = _elements
    for key, value in is_null_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key, '')
            if attribute is None:
                _elements.append(element)
        elements = _elements
    for key, value in is_true_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key, None)
            if attribute is True:
                _elements.append(element)
        elements = _elements
    for key, value in is_false_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key, None)
            if attribute is False:
                _elements.append(element)
        elements = _elements
    for key, value in in_list_filters.items():
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

    for key, value in not_in_list_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if value not in attribute.split(','):
                _elements.append(element)
        elements = _elements
    for key, value in not_substring_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key, None)
            if attribute is None:
                continue

            if value not in attribute:
                _elements.append(element)
        elements = _elements
    for key, value in not_starts_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if not attribute.startswith(value):
                _elements.append(element)
        elements = _elements
    for key, value in not_ends_with_filters.items():
        _elements = []
        for element in elements:
            attribute = element.get('tags', {}).get(key)
            if not attribute:
                continue

            if not attribute.endswith(value):
                _elements.append(element)
        elements = _elements

    return elements


def get_filter(args, filter_name, filter_key_prefix=None, valid_search_keys=None, bool_search_keys=None):
    filters = {}
    unused_args = {}
    for key, value in args.items():
        if bool_search_keys and key in bool_search_keys:
            value = to_bool(value)

        if filter_name == 'tags.exact' and key.startswith('tags.') and not key.startswith('tags.exact.'):
            key = 'tags.exact.{0}'.format(key.replace('tags.', ''))
        elif filter_name == 'exact' and not key.startswith('exact.') and '.' not in key:
            if valid_search_keys and key.replace('exact.', '') not in valid_search_keys:
                unused_args[key] = value
                continue
            key = 'exact.{0}'.format(key.replace('exact.', ''))
        elif not key.startswith('{0}.'.format(filter_name)):
            unused_args[key] = value
            continue

        length = len(filter_name) + 1
        filter_key_lookup = key[length:]
        filter_key = filter_key_lookup

        if valid_search_keys and filter_key_lookup in valid_search_keys:
            filters[filter_key] = value
        elif not valid_search_keys:
            filters[filter_key] = value

    return filters, unused_args
