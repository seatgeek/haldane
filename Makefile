# changing this variable may result in the virtualenv being created incorrectly
# it should match the service name
APP_NAME = haldane

ifndef PORT
	PORT = 5000
endif

include common.Makefile

.PHONY: requirements
requirements: ## installs system requirements
	sudo apt-get install -qq -y --force-yes libevent-dev > /dev/null

.PHONY: test
test: validate-amqp-dispatcher-config ## runs tests
	export SG_ENV=test && $(NOSE)

.PHONY: travis
travis: test ## runs tests for travis

.PHONY: server
server: ## starts the built-in server
	export DEBUG=1 && $(PYTHON) application.py

.PHONY: gunicorn
gunicorn: ## starts the gunicorn server
	$(GUNICORN) -w 2 -b :$(PORT) --worker-class gevent --logger-class haldane.glogging.Logger haldane:make_application\(\)
