# haldane

a friendly http interface to the ec2 api

## Requirements

- Vagrant
- Virtualbox
- 1 gigabytes of free ram

## Installation

Once you have vagrant and virtualbox installed, you can bring up a vm with the service installed:

```bash
cd path/to/haldane
vagrant up
```

By default, this will use `vmware_fusion` as the vagrant provider, though using you can also use `virtualbox`:

```bash
vagrant up --provider virtualbox
```

## Running

You can ssh onto the box and run the webservice:

```bash
vagrant ssh
source .env && make server
```

The webservice will now be running and exposed to the host machine at `http://localhost:5000`

> Note that you may wish to change the configuration in use. You can do so by modifying the .env.test file with your configuration.

## Tests

All tests run with `SG_ENV=test`. You can run tests within the vm:

```bash
# a .env file does not exist, you will need to create one
vagrant ssh
source .env && make test
```

## Endpoints:

- `/`: Healthcheck
- `/_status`: Healthcheck
- `/nodes/<region>?q=<query>`: List all nodes
  - `region` (optional): Filter to a specific region
  - `query` (optional): Substring to search node names by before returning the resultset
- `/nodes/group/<group>?region=us-east-1&query=<query>`: List all nodes grouped by autoscale group
  - `group` (optional): An autoscale group name to filter by
  - `region` (optional): Filter to a specific region
  - `query` (optional): Substring to search node names by before returning the resultset

## How it works

This services uses `boto` underneath to provide an api listing all nodes available in a given EC2 account. It is intended to be used as a replacement for hitting the EC2 api directly, as that can be slow at times.
