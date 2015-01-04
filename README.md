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
  - `query` (optional): Substring to search node names by before returning the resultset
  - `region` (optional): Filter to a specific region
  - `status` (optional): Filter to specific node status
- `/nodes/group/<group>?region=us-east-1&query=<query>`: List all nodes grouped by autoscale group
  - `group` (optional): An autoscale group name to filter by
  - `query` (optional): Substring to search node names by before returning the resultset
  - `region` (optional): Filter to a specific region
  - `status` (optional): Filter to specific node status

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
