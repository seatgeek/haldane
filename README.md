
a friendly http interface to the ec2 api

## Requirements

- Vagrant
- VMWare Fusion
- 1 gigabytes of free ram
- Python 2.7.8 or below due to a bug in 2.7.9 SSL

## Installation

> OS X Users are assumed to be running homebrew. Please set that up before continuing.
> Our makefile should install everything necessary to run this service within a Ubuntu 14.04 or Mac OS X 10.9+ environment.

### On a VM

Once you have vagrant and virtualbox installed, you can bring up a vm with the service installed:

```bash
cd path/to/haldane
vagrant up
```

By default, this will use `vmware_fusion` as the vagrant provider, though using you can also use `virtualbox`:

```bash
vagrant up --provider virtualbox
```

### Manually

You will need to setup a few system-level dependencies first. You can do this using the following make target:

```shell
# install system-level dependencies first
# may ask for sudo permissions to install certain packages
make requirements

# now create a python virtual environment with all the required packages
# will ask for sudo permissions to install virtualenv if it is not available
# the path is set to `.virtualenv` by default, though we respect
# the following environment variables:
# - `WORKON_HOME`
# - `VIRTUALENV_PATH`
make venv

# activate the virtualenv:
eval $(make venv-activate)

# to deactivate the virtualenv, run the following command:
deactivate

# for more actions you can perform, just run the `make` or `make help` commands
```

## Running

You can ssh onto the box and run the webservice:

```bash
vagrant ssh
source .env && make server
```

The webservice will now be running and exposed to the host machine at `http://localhost:5000`

> Note that you may wish to change the configuration in use. You can do so by modifying the .env.test file with your configuration.

## Configuration

All configuration is set via environment variables. The following environment variables are available for use:

- `ALLOWED_IPS`: (Default: None) A comma-separated list of ip addresses that can basic authentication.
- `ALTERNATIVE_AUTOSCALE_TAG_NAME`: (Default: None) A tag that can be used as an alternative to the AWS group name to categorize instances.
- `AWS_API_VERSION`: (Default: `2016-09-15`) The default api version to use when retrieving instance type.
- `AWS_ACCESS_KEY_ID`: (Default: None) An AWS access key id
- `AWS_REGIONS`: (Default: us-east-1) A comma-separated list of regions to query for.
- `AWS_SECRET_ACCESS_KEY`: (Default: None) An AWS secret access key
- `BASIC_AUTH`: (Default: None) A list of basic auth user/password combinations. The format for each is `username:password`.
- `BOOLEAN_AWS_TAG_ATTRIBUTES`: (Default: None) A comma-separated list of instance tags that will be pulled out as top-level instance attributes set and converted into booleans.
- `BUGSNAG_API_KEY`: (Default: None) An api key for reporting errors to bugsnag.
- `CACHE_EXPIRATION`: (Default: `180`) Time in seconds until a cached AWS api retrieval expires.
- `CACHE_SIZE`: (Default: `1024`) Max number of items to cache in the LRU cache. Can be safely set to 2.
- `DEBUG`: (Default: `0`) Whether to turn on debug mode or not.
- `LISTEN_INTERFACE`: (Default: `0.0.0.0`) The interface which the server will bind to.
- `PORT`: (Default: `5000`) Server port.
- `SENTRY_DSN`: (Default: None) An DSN for reporting errors to sentry.
- `TOP_LEVEL_AWS_TAG_ATTRIBUTES`: (Default: None) A comma-separated list of instance tags that will be pulled out as top-level instance attributes set.

The AWS policy is fairly small, and an `iam-profile.json` is provided in this repository in the case that you wish to lock down permissions to only those necessary.

## Endpoints:

- `/`: Healthcheck
- `/_status`: Healthcheck
- `/amis?q=<query>&limit=<limit>`: List all amis owned by the user specified by the AWS credentials.
  - `format` (optional): If set to `list`, turns ami attributes from an object indexed by the name key to a list of those objects. Can also be set to `csv`. Defaults to `dict`.
  - `id` (optional): An image id to filter by (eg. `ami-21e750d9`)
  - `query` (optional): Substring to search ami names by before returning the resultset
  - `region` (optional): Filter to a specific region
- `/instance-types/<api-version>`: List all instance types available for a specific api version (version is optional).
- `/nodes/<region>?q=<query>&limit=<limit>&status=<status>&group=<group>`: List all nodes
  - `format` (optional): If set to `list`, turns node attributes from an object indexed by the name key to a list of those objects. Can also be set to `csv`. Defaults to `dict`.
  - `limit` (optional): An integer to limit the resultset by
  - `query` (optional): Substring to search the `name` field by before returning the resultset
- `/nodes/group/<group>?region=<region>&query=<query>&status=<status>`: List all nodes grouped by autoscale group
  - `format` (optional): If set to `list`, turns node attributes from an object indexed by the name key to a list of those objects.
  - `query` (optional): Substring to search node names by before returning the resultset
- `/rds-instances/<region>?q=<query>&limit=<limit>&status=<status>`: List all nodes
  - `format` (optional): If set to `list`, turns node attributes from an object indexed by the name key to a list of those objects. Can also be set to `csv`. Defaults to `dict`.
  - `limit` (optional): An integer to limit the resultset by
  - `query` (optional): Substring to search the `name` field by before returning the resultset

### Filters

Field values that are *exactly* one of the following strings are transformed into their language "equivalents":

- `none`
- `nil`
- `none`
- `true`
- `false`

> The values are lowercased before the check is performed.

The following attributes filters are globally available:

- `availability_zone` (optional): An availability zone to filter by (eg. `us-east-1a`)
- `id` (optional): An instance id to filter by (eg. `i-21e750d9`)
- `name` (optional): A name to filter by (eg. `graphite-ec2-01`)
- `region` (optional): Filter to a specific region (eg. `us-east-1`)
- `status` (optional): Filter to specific node status (eg. `terminated`)

The following attribute filters are available for the `/nodes` and `/nodes/group` endpoints:

- `elastic_ip` (optional): Whether or not to filter to just instances with an elastic_ip
- `group` (optional): An autoscale group name to filter by
- `image_id` (optional): An image id to filter by (eg. `ami-123abc4d`)
- `image_name` (optional): An image name to filter by (eg. `BaseAMI`)
- `instance_type` (optional): Filter to a specific instance type (eg. `t2.large`)
- `instance_class` (optional): Filter to a specific instance type (eg. `t2`)
- `instance_profile_id` (optional): Filter to a specific instance profile id (eg. `O34RQ3IUIO3FOUI3F`)
- `instance_profile_name` (optional): Filter to a specific instance profile name (eg. `Production-Api`)
- `ip_address` (optional): Filter to a specific private ip address (eg. `54.10.2.20`)
- `private_ip_address` (optional): Filter to a specific private ip address (eg. `10.10.2.20`)
- `vpc_id` (optional): Filter to specific vpc (eg. `vpc-8675309`)

The following attribute filters are available for the `/rds-instances` endpoint:

- `allocated_storage` (optional)
- `auto_minor_version_upgrade` (optional)
- `backup_retention_period` (optional)
- `ca_certificate_identifier` (optional)
- `copy_tags_to_snapshot` (optional)
- `db_instance_arn` (optional)
- `db_instance_class` (optional)
- `db_instance_port` (optional)
- `db_instance_status` (optional)
- `db_name` (optional)
- `dbi_resource_id` (optional)
- `engine` (optional)
- `engine_version` (optional)
- `enhanced_monitoring_resource_arn` (optional)
- `license_model` (optional)
- `master_username` (optional)
- `monitoring_interval` (optional)
- `monitoring_role_arn` (optional)
- `multi_az` (optional)
- `preferred_backup_window` (optional)
- `preferred_maintenance_window` (optional)
- `publicly_accessible` (optional)
- `secondary_availability_zone` (optional)
- `storage_encrypted` (optional)
- `storage_type` (optional)

#### Field Filtering

Fields in the response body can be filtered using the `fields` querystring argument. Fields are a `comma-separated` list of any of the attributes already returned. Tags cannot be filtered on a per-tag basis, though you may choose to include or exclude the `tags` attribute entirely.

```bash
curl http://localhost:5000/nodes?fields=id,image_name
```

#### Complex Filters

Filtering is performed *after* retrieving results from the EC2 API. The following are valid filters:

- `exact`: performs an exact match on the value of the tag name
- `in-list`: splits the tag value by comma and verifies that the passed value is in the resulting list
- `is-null`: checks if the value is `null`
- `is-true`: checks if the value is `true`
- `is-false`: checks if the value is `false`
- `substring`: performs a substring match on the value of the tag name
- `ends-with`: performs a match using `endswith` on the value of the tag name
- `starts-with`: performs a match using `startswith` on the value of the tag name
- `not-in-list`: splits the tag value by comma and verifies that the passed value is *not* in the resulting list
- `not-substring`: performs an inverse substring match on the value of the tag name
- `not-ends-with`: performs an inverse match using `endswith` on the value of the tag name
- `not-starts-with`: performs an inverse match using `startswith` on the value of the tag name

A simple example is as follows

```bash
curl http://localhost:5000/nodes?substring.name=www
```

#### Tag Filtering

You can also filter by tags by using the `tags.FILTER.TAG_NAME` querystring pattern as follows:

```bash
curl http://localhost:5000/nodes?tags.exact.bootstrapped=true&tags.substring.Name=admin
```

You may also specify an exact match filter when omitting the `FILTER` section like so:

```bash
curl http://localhost:5000/nodes?tags.bootstrapped=true
```

#### Filtering by the status field

Valid `status` values are as follows:

- `pending`
- `running`
- `shutting-down`
- `terminated`
- `stopping`
- `stopped`

```bash
curl http://localhost:5000/nodes?status=running
```

#### Errors

If an invalid querystring argument is passed, a `json` response similar to the following will be sent from the service:

```javascript
{
  detail: "Invalid region querystring argument passed.",
  status: 400,
  title: "Invalid argument passed"
}
```

The following errors are possible:

- Invalid region querystring argument
- Invalid status querystring argument
- General EC2ResponseError

## How it works

This services uses `boto3` underneath to provide an api listing all nodes available in a given EC2 account. It is intended to be used as a replacement for hitting the EC2 api directly, as that can be slow at times.

## Caveats

When using the `/nodes` or `/nodes/group` endpoints with a format of `dict`, the response is keyed by the `Name` tag of the ec2 instance. If you have multiple servers with the same value for the `Name` tag, this may result in "hidden" servers. If a server is not running, it will be hidden by default, otherwise it may overwrite the previous entry. This will both be logged in the `haldane` logging output *and* will be surfaced as `meta.hidden_nodes`, regardless of the endpoint being used.
