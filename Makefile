ifndef VIRTUALENV_PATH
	VIRTUALENV_PATH = .virtualenv
endif
VIRTUALENV_BIN = $(VIRTUALENV_PATH)/bin

AMQP_DISPATCHER = $(ENV) $(VIRTUALENV_BIN)/amqp-dispatcher
DEBIAN_FRONTEND = noninteractive
DEV_ENV = source $(VIRTUALENV_BIN)/activate ;
FAB = $(VIRTUALENV_BIN)/fab
GUNICORN = $(ENV) $(VIRTUALENV_BIN)/gunicorn
NOSE = $(VIRTUALENV_BIN)/nosetests
PIP = $(VIRTUALENV_BIN)/pip
PIP_ACCEL = $(VIRTUALENV_BIN)/pip-accel
PYCURL_SSL_LIBRARY = openssl
PYTHON = $(ENV) $(VIRTUALENV_BIN)/python

# If the first argument is "fab"...
ifeq (fab,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "fab"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

.PHONY: requirements
requirements:
	sudo apt-get install -qq -y --force-yes libevent-dev > /dev/null

.PHONY: services
services:
	echo "no services to setup"

.PHONY: database
database:
	echo "no databases to setup"

.PHONY: venv
venv:
	sudo pip install pip==1.4.1 > /dev/null
	sudo pip install virtualenv > /dev/null
	if [ ! -f $(PIP_ACCEL) ]; then virtualenv --distribute $(VIRTUALENV_PATH) > /dev/null; fi
	$(PIP) install pip-accel==0.13.5 > /dev/null
	$(PIP_ACCEL) install pip==1.4.1 > /dev/null
	export PYCURL_SSL_LIBRARY=openssl && $(PIP_ACCEL) install -r requirements.txt --use-mirrors > /dev/null
	$(PIP_ACCEL) install nose==1.3.3 > /dev/null
	$(PIP_ACCEL) install coveralls > /dev/null

.PHONY: test
test:
	$(PIP) install nose==1.3.3 > /dev/null
	export SG_ENV=test && $(NOSE)

.PHONY: server
server:
	$(PYTHON) application.py

.PHONY: gunicorn
gunicorn:
	$(GUNICORN) -w 2 -b :5000 haldane:make_application\(\)
