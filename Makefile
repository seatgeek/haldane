VIRTUALENV_PATH = .virtualenv
VIRTUALENV_BIN = $(VIRTUALENV_PATH)/bin

DEV_ENV = source $(VIRTUALENV_BIN)/activate ;
NOSE = $(VIRTUALENV_BIN)/nosetests
PIP = $(VIRTUALENV_BIN)/pip
PYTHON = $(ENV) $(VIRTUALENV_BIN)/python
AMQP_DISPATCHER = $(ENV) $(VIRTUALENV_BIN)/amqp-dispatcher
GUNICORN = $(ENV) $(VIRTUALENV_BIN)/gunicorn
DEBIAN_FRONTEND = noninteractive

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
	if [ ! -f $(PIP) ]; then virtualenv --distribute $(VIRTUALENV_PATH) > /dev/null; fi
	$(PIP) install pip==1.4.1 > /dev/null
	$(PIP) install -r requirements.txt > /dev/null

.PHONY: test
test:
	$(PIP) install nose==1.3.3 > /dev/null
	export SG_ENV=test && $(NOSE)

.PHONY: server
server:
	$(PYTHON) runserver.py

.PHONY: gunicorn
gunicorn:
	$(GUNICORN) -w 2 -b :5000 haldane:make_application\(\)
