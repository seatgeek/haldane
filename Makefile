# changing this variable may result in the virtualenv being created incorrectly
# it should match the service name
APP_NAME = haldane

ifndef PORT
	PORT = 5000
endif

include common.Makefile

.PHONY: requirements
requirements: ## installs system requirements
ifeq ($(BREW),)
ifndef TRAVIS
	$(MAKE) aptfile
endif
else
	brew tap | grep -q '^homebrew/bundle$$' || brew tap homebrew/bundle
	brew bundle
endif

.PHONY: server
server: ## starts the built-in server
	export DEBUG=1 && $(PYTHON) application.py

.PHONY: gunicorn
gunicorn: ## starts the gunicorn server
	$(GUNICORN) -w $(WEB_CONCURRENCY) -b :$(PORT) --worker-class gevent --logger-class app.glogging.Logger app:make_application\(\) --error-logfile - --log-file -

.PHONY: heroku
heroku: ## starts the gunicorn server for heroku
	newrelic-admin run-program $(GUNICORN) -w $(WEB_CONCURRENCY) -b :$(PORT) --worker-class gevent --logger-class app.glogging.Logger app:make_application\(\) --error-logfile - --log-file -

.PHONY: test
test: ## runs tests via pytest
	$(VIRTUALENV_BIN)/pytest
