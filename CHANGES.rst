Changelog
=========

0.2.1 (2017-07-17)
------------------

Fix
~~~

- Lazy-import flask. [Jose Diaz-Gonzalez]

0.2.0 (2017-07-17)
------------------

Fix
~~~

- Update README.rst to pass rst-lint. [Jose Diaz-Gonzalez]

- Ensure we allow setting fields to something that doesn’t include `id`
  [Jose Diaz-Gonzalez]

- Add missing comma. [Jose Diaz-Gonzalez]

- Correct in-list filter. [Jose Diaz-Gonzalez]

- Add missing import. [Jose Diaz-Gonzalez]

- Do not include name when specified fields do not contain it. [Jose
  Diaz-Gonzalez]

- Properly pull out fields. [Jose Diaz-Gonzalez]

- Properly initialize sentry. [Jose Diaz-Gonzalez]

- Use regular server. [Jose Diaz-Gonzalez]

- Use makefile inside of Procfile. [Jose Diaz-Gonzalez]

- Do not attempt to iterate over NoneType. [Jose Diaz-Gonzalez]

- Revert bugsnag upgrade. [Jose Diaz-Gonzalez]

- Pass in werkzeug.datastructures.ImmutableMultiDict for filter_elements
  test. [Jose Diaz-Gonzalez]

- Swap to ImmutableMultiDict. [Jose Diaz-Gonzalez]

- Check type before calling to_dict. [Jose Diaz-Gonzalez]

- Use correct argument name. [Jose Diaz-Gonzalez]

- Allow ALLOWED_IPS to be an empty string. [Jose Diaz-Gonzalez]

- Use correct check - format may not always have a value. [Jose Diaz-
  Gonzalez]

Other
~~~~~

- Feat: allow making releases of haldane. [Jose Diaz-Gonzalez]

- Feat: add a Dockerfile for building and running haldane within docker.
  [Jose Diaz-Gonzalez]

- Feat: prepare for pypi support. [Jose Diaz-Gonzalez]

- Feat: respect VIRTUALENV_PATH and do not write profile.sh if using
  relative url. [Jose Diaz-Gonzalez]

- Feat: allow retrieval of rds instance tags. [Jose Diaz-Gonzalez]

- Feat: update common.Makefile. [Jose Diaz-Gonzalez]

- Docs: remove duplicated filter value on README.md. [Eric Büttner]

- Docs: add missing header. [Jose Diaz-Gonzalez]

- Chore: upgrade dependencies. [Jose Diaz-Gonzalez]

- Add BSD 3-Clause License. [Jose Diaz-Gonzalez]

- Feat: alias /nodes to /instances. [Jose Diaz-Gonzalez]

- Docs: update the necessary iam-profile.json. [Jose Diaz-Gonzalez]

- Feat: implement /rds-instances. [Jose Diaz-Gonzalez]

- Chore: remove extra imports. [Jose Diaz-Gonzalez]

- Tests: cleanup. [Jose Diaz-Gonzalez]

- Feat: add make test target. [Jose Diaz-Gonzalez]

- Feat: add top-level aws tag attributes. [Jose Diaz-Gonzalez]

- Feat: implement csv responses. [Jose Diaz-Gonzalez]

- Docs: document ip filters. [Jose Diaz-Gonzalez]

- Feat: allow filtering by ip addresses. [Jose Diaz-Gonzalez]

- Feat: add the ability to list instance types. [Jose Diaz-Gonzalez]

- Refactor: move non-web endpoints to aws.py. [Jose Diaz-Gonzalez]

- Feat: redirect *all* output. [Jose Diaz-Gonzalez]

- Feat: use app.glogging.Logger for gunicorn. [Jose Diaz-Gonzalez]

- Feat: use gevent worker class. [Jose Diaz-Gonzalez]

- Feat: respect PORT env variable when running procfile. [Jose Diaz-
  Gonzalez]

- Refactor: drop use of boto in favor of boto3. [Jose Diaz-Gonzalez]

  Also remove a few attributes that are no longer easily available


- Feat: minor changes to makefile for better vagrant support. [Jose
  Diaz-Gonzalez]

  Also do not force vmware


- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Revert "chore: upgrade dependency" [Jose Diaz-Gonzalez]

  This reverts commit 6c4a6bca42bab7c3be32f3a9ab85e979068422f2.


- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Chore: upgrade dependency. [Jose Diaz-Gonzalez]

- Feat: upgrade boto. [Jose Diaz-Gonzalez]

- Chore: pip freeze > requirements.txt. [Jose Diaz-Gonzalez]

- Feat: fix filtering by query. [Jose Diaz-Gonzalez]

- Feat: add tests for filter_elements. [Jose Diaz-Gonzalez]

- Docs: update dummy vpc id. [Jose Diaz-Gonzalez]

- Chore: pip freeze > requirements.txt. [Jose Diaz-Gonzalez]

- Tests: implement first set of tests. [Jose Diaz-Gonzalez]

- Refactor: move filtering into it’s own module. [Jose Diaz-Gonzalez]

- Feat: upgrade dependencies. [Jose Diaz-Gonzalez]

- Feat: add filtering by instance profile id and name. [Jose Diaz-
  Gonzalez]

- Docs: document filtering by vpc_id. [Jose Diaz-Gonzalez]

- Feat: add is-false, is-true, and is-null filtering. [Jose Diaz-
  Gonzalez]

- Feat: allow filtering by boolean attributes. [Jose Diaz-Gonzalez]

- Feat: cast tags to primitive types. [Jose Diaz-Gonzalez]

- Feat: add filtering via vpc_id. [Jose Diaz-Gonzalez]

- Chore: fix pep8 issues. [Jose Diaz-Gonzalez]

- Feat: add negated filters. [Jose Diaz-Gonzalez]

- Refactor: changeup how filters are retrieved in order to make it
  easier to expand the filterset. [Jose Diaz-Gonzalez]

- Feat: add fields filtering. [Jose Diaz-Gonzalez]

- Feat: implement startswith and endswith filtering. [Jose Diaz-
  Gonzalez]

- Add image_name as a filter and refactor filtering. [Jose Diaz-
  Gonzalez]

- Refactor boolean search keys to extra env var. [Jose Diaz-Gonzalez]

- Add /amis endpoint. [Jose Diaz-Gonzalez]

- Better tag filtering. [Jose Diaz-Gonzalez]

- Add more info to status page. [Jose Diaz-Gonzalez]

- Add filtering by image_id. [Jose Diaz-Gonzalez]

- A bit of cleanup and documentation updates. [Jose Diaz-Gonzalez]

- Cleanup local development. [Jose Diaz-Gonzalez]

- Add filtering by id. [Jose Diaz-Gonzalez]

- Move namespace from haldane to app. [Jose Diaz-Gonzalez]

- Respect WEB_CONCURRENCY env var in Makefile. [Jose Diaz-Gonzalez]

- Log errors to stderr. [Jose Diaz-Gonzalez]

- Set worker class to gevent. [Jose Diaz-Gonzalez]

- Use custom logger for gunicorn. [Jose Diaz-Gonzalez]

- Provide overridden logging formats for the gunicorn logger. [Jose
  Diaz-Gonzalez]

- Patch all logging output to have the same prefix. [Jose Diaz-Gonzalez]

- Upgrade all requirements. [Jose Diaz-Gonzalez]

- Refactor node handling to expose that certain nodes are being hidden.
  [Jose Diaz-Gonzalez]

  Because of the way dict indexing works, some nodes (non-running or "existing") will be hidden from the output.

  This changes makes that decision visible to users, and also allows us to expose *all* elements when using list formatting.


- Clean up docs a bit. [Jose Diaz-Gonzalez]

- Filter out empty strings from config lists. [Jose Diaz-Gonzalez]

- Allow specifying multiple tags as top-level boolean attributes. [Jose
  Diaz-Gonzalez]

- Allow configuring the key that is used for the default autoscale group
  tag name. [Jose Diaz-Gonzalez]

- Fix name setting when there is no group. [Jose Diaz-Gonzalez]

- Fix instance class. [Jose Diaz-Gonzalez]

- Add the ability to filter by instance_class. [Jose Diaz-Gonzalez]

- Refactor filtering to "simplify" loops. [Jose Diaz-Gonzalez]

- Fix PEP8 binary call wrapper. [Jose Diaz-Gonzalez]

- Respect VIRTUAL_ENV env var for VIRTUALENV_PATH. [Jose Diaz-Gonzalez]

- Add nose requirement. [Jose Diaz-Gonzalez]

- Refactor common make tasks into common.Makefile. [Jose Diaz-Gonzalez]

- Fix auth check skipping. [Jose Diaz-Gonzalez]

- Add logging. [Jose Diaz-Gonzalez]

- Allow skipping basic auth checks for certain ips. [Jose Diaz-Gonzalez]

- Ensure we don't overwrite existing instances with non-running
  duplicates. [Jose Diaz-Gonzalez]

- Add ability to show and filter by elastic ip. [Jose Diaz-Gonzalez]

- Fix conditional. [Jose Diaz-Gonzalez]

- Sort keys. [Jose Diaz-Gonzalez]

- Create name once. [Jose Diaz-Gonzalez]

- Add vpc_id and az. [Jose Diaz-Gonzalez]

- Pip freeze > requirements.txt. [Jose Diaz-Gonzalez]

- Use new bento/ubuntu-14.04 box [ci skip] [Jose Diaz-Gonzalez]

- Also respect seatgeek-specific group. [Jose Diaz-Gonzalez]

- Sync vagrant config with other services. [Jose Diaz-Gonzalez]

- Add instance launch_time. [Jose Diaz-Gonzalez]

- Fix instance_type retrieval. [Jose Diaz-Gonzalez]

- Add support for filtering by instance_type. [Jose Diaz-Gonzalez]

- Add `format` key. [Jose Diaz-Gonzalez]

- Remove unused env var. [Jose Diaz-Gonzalez]

- Lock Werkzeug to a working version.. [Jose Diaz-Gonzalez]

- Add filtering by group query string argument. [Jose Diaz-Gonzalez]

- Add filtering by tags. [Jose Diaz-Gonzalez]

- Add a few more querystring args. [Jose Diaz-Gonzalez]

- Add tags to node dictionary. [Jose Diaz-Gonzalez]

- Add `limit` querystring argument to `/nodes/<group>` endpoint. [Jose
  Diaz-Gonzalez]

  Also add a `per_page` meta response key


- Add filtering by instance status. [Jose Diaz-Gonzalez]

- Document error responses and add an error state for invalid region
  querystring arguments. [Jose Diaz-Gonzalez]

- Refactor sort_by_group to handle a group-limiting argument. [Jose
  Diaz-Gonzalez]

- Do not allow invalid regions to be specified. [Jose Diaz-Gonzalez]

- Add support for `q` shorthand for `query` querystring arg. [Jose Diaz-
  Gonzalez]

- Clock => time. [Jose Diaz-Gonzalez]

- Add timing to the api response. [Jose Diaz-Gonzalez]

- Use a custom logger in handle_ec2_response_error() [Jose Diaz-
  Gonzalez]

- Only handle errors for the BugsnagHandler. [Jose Diaz-Gonzalez]

- Specify older runtime. [Jose Diaz-Gonzalez]

- Remove bad requirement. [Jose Diaz-Gonzalez]

- Use a forked gevent. [Jose Diaz-Gonzalez]

- Add newrelic integration. [Jose Diaz-Gonzalez]

- Add support for Bugsnag as an alternative to Sentry. [Jose Diaz-
  Gonzalez]

- Move basic auth code to it's own module. [Jose Diaz-Gonzalez]

- Hack to avoid "Imported but not used" validation issue. [Jose Diaz-
  Gonzalez]

- Add workaround for python 2.7.9 not having sslwrap in the _ssl module.
  [Jose Diaz-Gonzalez]

- Escape parens. [Jose Diaz-Gonzalez]

- Switch back to gunicorn. [Jose Diaz-Gonzalez]

- Upgrade to eventlet 0.16 to improve python compatibility. [Jose Diaz-
  Gonzalez]

- Try to use another way to start the server... [Jose Diaz-Gonzalez]

- Do not escape parens. [Jose Diaz-Gonzalez]

- Add .editorconfig. [Jose Diaz-Gonzalez]

- Add more env vars. [Jose Diaz-Gonzalez]

- Use number of workers set in WEB_CONCURRENCY. [Jose Diaz-Gonzalez]

- Do not specify workers. [Jose Diaz-Gonzalez]

- Add procfile. [Jose Diaz-Gonzalez]

- Correctly handle cases where BASIC_AUTH is not configured. [Jose Diaz-
  Gonzalez]

- Properly catch all EC2ResponseError exceptions. [Jose Diaz-Gonzalez]

- Handle specifying a single group in the /nodes/group endpoint. [Jose
  Diaz-Gonzalez]

- Make the region a querystring value. [Jose Diaz-Gonzalez]

- Move all json response creation into a custom method. [Jose Diaz-
  Gonzalez]

- Add basic auth support. [Jose Diaz-Gonzalez]

- Add request logging for gunicorn requests. [Jose Diaz-Gonzalez]

- Set default regions to both east and west. [Jose Diaz-Gonzalez]

- Conform to app spec for elastic beanstalk python apps. [Jose Diaz-
  Gonzalez]

  There should be an application.py that exports an `application` module


- Allow configurable listen interface. [Jose Diaz-Gonzalez]

- Add ebs-deploy requirement. [Jose Diaz-Gonzalez]

- Extend gitignore for vagrant setup. [Jose Diaz-Gonzalez]

- Initial commit. [Jose Diaz-Gonzalez]


