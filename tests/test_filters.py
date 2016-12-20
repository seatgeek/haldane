from app.filters import filter_elements
from app.filters import filter_by_tags
from app.filters import get_filter

def test_get_filters():
    args = {
        'tags.exact.tag-with-prefix': 1,
        'tags.exact-tag-sans-prefix': 1,
        'exact.with-prefix': 1,
        'exact-sans-prefix': 1,
        'not-exact.prefix': 1,
        'in-list.suffix': 1
    }
    filters, unused_args = get_filter(args, 'tags.exact')
    assert len(filters) == 2
    assert len(unused_args) == 4
    filters, unused_args = get_filter(args, 'tags.exact', valid_search_keys=['tag-with-prefix'])
    assert len(filters) == 1
    assert len(unused_args) == 4

    filters, unused_args = get_filter(args, 'exact')
    assert len(filters) == 2
    assert len(unused_args) == 4
    filters, unused_args = get_filter(args, 'exact', valid_search_keys=['with-prefix'])
    assert len(filters) == 1
    assert len(unused_args) == 5

    filters, unused_args = get_filter(args, 'in-list')
    assert len(filters) == 1
    assert len(unused_args) == 5
    filters, unused_args = get_filter(args, 'in-list', valid_search_keys=['suffix'])
    assert len(filters) == 1
    assert len(unused_args) == 5
    filters, unused_args = get_filter(args, 'in-list', valid_search_keys=['another-suffix'])
    assert len(filters) == 0
    assert len(unused_args) == 5

def test_filter_by_tags():
    elements = elements_fixture()
    filtered = filter_by_tags(elements, {'tags.exact.environment': 'production'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.environment': 'production'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.in-list.apps': 'www'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.in-list.apps': 'admin'})
    assert len(filtered) == 0
    filtered = filter_by_tags(elements, {'tags.is-null.UbuntuVersion': ''})
    assert len(filtered) == 2
    filtered = filter_by_tags(elements, {'tags.is-true.provisioned': ''})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.is-false.provisioned': ''})
    assert len(filtered) == 0
    filtered = filter_by_tags(elements, {'tags.substring.environment': 'prod'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.ends-with.environment': 'tion'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.ends-with.environment': 'ing'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.starts-with.environment': 'prod'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.starts-with.environment': 'stag'})
    assert len(filtered) == 1

def test_filter_by_tags_negated():
    elements = elements_fixture()
    filtered = filter_by_tags(elements, {'tags.not-in-list.apps': 'www'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.not-in-list.apps': 'admin'})
    assert len(filtered) == 2
    filtered = filter_by_tags(elements, {'tags.not-substring.environment': 'prod'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.not-ends-with.environment': 'tion'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.not-ends-with.environment': 'ing'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.not-starts-with.environment': 'prod'})
    assert len(filtered) == 1
    filtered = filter_by_tags(elements, {'tags.not-starts-with.environment': 'stag'})
    assert len(filtered) == 1


def elements_fixture():
    return [
        {
            "availability_zone": "us-east-1a",
            "elastic_ip": False,
            "group": "www",
            "id": "i-abcdefgh",
            "image_id": "ami-1234abcd",
            "image_name": "",
            "instance_class": "m4",
            "instance_profile_id": None,
            "instance_profile_name": None,
            "instance_type": "m4.large",
            "ip_address": "",
            "launch_time": "2016-08-27T20:58:00.000Z",
            "name": "www-i-abcdefgh",
            "private_ip_address": "10.10.2.20",
            "region": "us-east-1",
            "status": "running",
            "tags": {
            "Name": "www-i-abcdefgh",
                "Name": "bee-wxyz7890",
                "aws:autoscaling:groupName": "www",
                "apps": "api,www",
                "environment": "production",
                "provisioned": True,
                "UbuntuVersion": None,
            },
            "vpc_id": None
        },
        {
            "availability_zone": "us-east-1b",
            "elastic_ip": False,
            "group": None,
            "id": "i-stuvwxyz",
            "image_id": "ami-wxyz7890",
            "image_name": "",
            "instance_class": "m1",
            "instance_profile_id": None,
            "instance_profile_name": None,
            "instance_type": "m1.large",
            "ip_address": "",
            "launch_time": "2016-12-15T14:22:01.000Z",
            "name": "bee-stuvwxyz",
            "private_ip_address": "10.10.2.30",
            "region": "us-east-1",
            "status": "running",
            "tags": {
                "Name": "bee-wxyz7890",
                "apps": "bee",
                "environment": "staging",
                "UbuntuVersion": None,
            },
            "vpc_id": None
        },
    ]
