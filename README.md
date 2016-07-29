
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

The AWS policy is fairly small, and an `iam-profile.json` is provided in this repository in the case that you wish to lock down permissions to only those necessary.

## Endpoints:

- `/`: Healthcheck
- `/_status`: Healthcheck
- `/nodes/<region>?q=<query>&limit=<limit>&status=<status>&group=<group>`: List all nodes
  - `elastic_ip` (optional): Whether or not to filter to just instances with an elastic_ip
  - `format` (optional): If set to `list`, turns node attributes from an object indexed by the name key to a list of those objects. Defaults to `dict`.
  - `group` (optional): An autoscale group name to filter by
  - `id` (optional): An instance id to filter by (eg. `i-21e750d9`)
  - `instance_type` (optional): Filter to a specific instance type (eg. `t2.large`)
  - `instance_class` (optional): Filter to a specific instance type (eg. `t2`)
  - `limit` (optional): An integer to limit the resultset by
  - `query` (optional): Substring to search node names by before returning the resultset
  - `region` (optional): Filter to a specific region
  - `status` (optional): Filter to specific node status
- `/nodes/group/<group>?region=<region>&query=<query>&status=<status>`: List all nodes grouped by autoscale group
  - `elastic_ip` (optional): Whether or not to filter to just instances with an elastic_ip
  - `format` (optional): If set to `list`, turns node attributes from an object indexed by the name key to a list of those objects.
  - `group` (optional): An autoscale group name to filter by
  - `id` (optional): An instance id to filter by (eg. `i-21e750d9`)
  - `instance_type` (optional): Filter to a specific instance type (eg. `t2.large`)
  - `instance_class` (optional): Filter to a specific instance type (eg. `t2`)
  - `query` (optional): Substring to search node names by before returning the resultset
  - `region` (optional): Filter to a specific region
  - `status` (optional): Filter to specific node status

You can also filter by tags by using the `tags.TAG_NAME` querystring pattern as follows:

```bash
curl http://localhost:5000/nodes?tags.bootstrapped=true&tags.Name=admin
```

Tag filtering is performed via a substring match *after* retrieving results from the EC2 API.

Valid `status` values are as follows:

- `pending`
- `running`
- `shutting-down`
- `terminated`
- `stopping`
- `stopped`

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

This services uses `boto` underneath to provide an api listing all nodes available in a given EC2 account. It is intended to be used as a replacement for hitting the EC2 api directly, as that can be slow at times.

## Caveats

When using the `/nodes` or `/nodes/group` endpoints with a format of `dict`, the response is keyed by the `Name` tag of the ec2 instance. If you have multiple servers with the same value for the `Name` tag, this may result in "hidden" servers. If a server is not running, it will be hidden by default, otherwise it may overwrite the previous entry. This will both be logged in the `haldane` logging output *and* will be surfaced as `meta.hidden_nodes`, regardless of the endpoint being used.
