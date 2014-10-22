from flask import Flask


def make_application():
    from haldane.config import Config
    import haldane.views

    flask_app = Flask(__name__, static_url_path='')

    if not Config.SUPPRESS_SENTRY:
        from raven.contrib.flask import Sentry
        Sentry(flask_app)

    flask_app.config.from_object('haldane.config.Config')
    flask_app.register_blueprint(haldane.views.blueprint_http)
    haldane.views.blueprint_http.config = flask_app.config

    return flask_app
