ifneq ($(shell which brew),)
	VIRTUALENV_PATH = $(HOME)/.virtualenvs/$(APP_NAME)
endif

ifdef WORKON_HOME
	VIRTUALENV_PATH = $(WORKON_HOME)/$(APP_NAME)
endif

ifneq ($(wildcard .heroku/python/bin/python),)
	VIRTUALENV_PATH = .heroku/python
endif

ifndef VIRTUALENV_PATH
	VIRTUALENV_PATH = .virtualenv
endif
VIRTUALENV_BIN = $(VIRTUALENV_PATH)/bin

ifdef TRAVIS
	SUDO_PREFIX =
else
	SUDO_PREFIX = 'sudo'
endif

ifndef NUMBER_OF_HTTP_WORKERS
	NUMBER_OF_HTTP_WORKERS = 2
endif

ifndef TEST_NAME
	TEST_NAME =
endif

ifndef TEST_OPTIONS
	TEST_OPTIONS =
endif

ifndef WEB_CONCURRENCY
	WEB_CONCURRENCY = $(NUMBER_OF_HTTP_WORKERS)
endif

ifdef DYNO
	WORKER_CONNECTION = "--connection=pika"
endif

ifndef R_PATH
	R_PATH = .renv
endif

AMQP_DISPATCHER = $(ENV) $(VIRTUALENV_BIN)/amqp-dispatcher
BREW := $(shell which brew)
DEBIAN_FRONTEND = noninteractive
DEV_ENV = source $(VIRTUALENV_BIN)/activate ;
FAB = $(VIRTUALENV_BIN)/fab
GUNICORN = $(ENV) $(VIRTUALENV_BIN)/gunicorn
NOSE = $(VIRTUALENV_BIN)/nosetests
PEP8 = ($VIRTUALENV_BIN)/pep8
PIP = $(VIRTUALENV_BIN)/pip
PIP_VERSION = 8.1.2
PYCURL_SSL_LIBRARY = openssl
PYTHON = $(ENV) $(VIRTUALENV_BIN)/python
R_LIB = $(R_PATH)/lib
R_MIRROR = http://cran.rstudio.com
WHOAMI := $(shell whoami)

# If the first argument is "fab"...
ifeq (fab,$(firstword $(MAKECMDGOALS)))
	# use the rest as arguments for "fab"
	RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
	# ...and turn them into do-nothing targets
	$(eval $(RUN_ARGS):;@:)
endif

.PHONY: all
all: help ## outputs the help message

.PHONY: help
help: ## this help.
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-36s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: requirements venv ## runs requirements installation and virtualenv creation

.PHONY: aptfile
aptfile: ## runs the service's aptfile to install debian dependencies
ifeq ($(BREW),)
	which aptfile || (wget --quiet -O /tmp/aptfile_0.0.2_amd64.deb http://sg-vagrant.s3.amazonaws.com/aptfile/aptfile_0.0.2_amd64.deb && sudo dpkg -i /tmp/aptfile_0.0.2_amd64.deb)
	sudo -E ./aptfile
endif

.PHONY: clean
clean: ## delete the virtualenv and any ignored files
	rm -rf $(VIRTUALENV_PATH)
	git clean -fX
	rm -rf logs/*
	find . -name "*.pyc" -exec rm -rf {} \;

.PHONY: create_env_file
create_env_file: ## copies the contents of .env.sample into .env
	@cp -n .env.sample .env || true

.PHONY: fab
fab: ## executes a fab command
	$(FAB) $(RUN_ARGS)

.PHONY: honcho
honcho: ## starts honcho, the python-equivalent of the foreman process manager
	$(VIRTUALENV_BIN)/honcho start

.PHONY: pep8
pep8: ## runs pep8
	$(VIRTUALENV_BIN)/pep8 .

.PHONY: pyflakes
pyflakes: ## runs pyflakes
	$(VIRTUALENV_BIN)/pyflakes .

.PHONY: r
r: ## installs r dependencies and sets the R_LIB path in your ~/.Rprofile
	if [ ! -d $(R_LIB) ]; then mkdir -p $(R_LIB); fi > /dev/null
	@while read -r pkg; \
		do echo 'if (!require("'$$pkg'", character.only = TRUE)) { install.packages("'$$pkg'", repos="$(R_MIRROR)",quiet=TRUE,lib="$(R_LIB)") } ' > /tmp/r-$$pkg.R; \
		Rscript /tmp/r-$$pkg.R; \
		done < requirements.r > /dev/null
	echo '.libPaths("$(R_LIB)")' > ~/.Rprofile

.PHONY: validate-amqp-dispatcher-config
validate-amqp-dispatcher-config:  ## validates the amqp-dispatcher config yml file
	if [ -f amqp-dispatcher-config.yml ]; then PYTHONPATH=. amqp-dispatcher --validate --config amqp-dispatcher-config.yml; fi

.PHONY: venv
venv: ## creates a python virtualenv with your dependencies installed
ifeq ($(BREW),)
ifndef TRAVIS
	which pip || sudo pip install pip==$(PIP_VERSION) > /dev/null
	pip list | grep virtualenv || pip install virtualenv > /dev/null
endif
else
	which virtualenv || sudo pip install virtualenv > /dev/null
endif
	if [ ! -f $(PIP) ]; then virtualenv --distribute $(VIRTUALENV_PATH) > /dev/null; fi
	$(PIP) install --upgrade pip==$(PIP_VERSION) > /dev/null
	bash -c 'NUMPY=$$(grep numpy requirements.txt || true) ; if [[ ! -z "$$NUMPY" ]]; then $(PIP) install $$NUMPY; fi'
	export PYCURL_SSL_LIBRARY=openssl && export CFLAGS='-std=c99' && $(PIP) install -r requirements.txt > /dev/null
	bash -c 'NLTK=$$(grep nltk requirements.txt || true) ; if [[ ! -z "$$NLTK" ]]; then $(PYTHON) -m nltk.downloader punkt stopwords; fi'
ifeq ($(BREW),)
ifndef TRAVIS
	sudo sh -c 'echo "source $(VIRTUALENV_BIN)/activate" > /etc/profile.d/$(APP_NAME).sh'
	sudo sh -c 'echo "export PYTHONPATH=$(VIRTUALENV_PATH)/lib/python2.7/site-packages" >> /etc/profile.d/$(APP_NAME).sh'
endif
endif

.PHONY: venv-activate
venv-activate:  ## outputs a command that can be eval'd to activate the python virtualenv
	@echo "source $(VIRTUALENV_BIN)/activate"

.PHONY: worker
worker: ## runs the amqp-dispatcher worker
	if [ -f .env ]; then . ./.env; fi ; export PYTHONPATH=. && $(AMQP_DISPATCHER) --config=amqp-dispatcher-config.yml $(WORKER_CONNECTION)
