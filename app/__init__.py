from flask import Flask


def make_application():
    from app.config import Config
    import app.views

    flask_app = Flask(__name__, static_url_path='')

    if Config.BUGSNAG_API_KEY:
        import bugsnag
        from bugsnag.flask import handle_exceptions
        bugsnag.configure(api_key=Config.BUGSNAG_API_KEY)
        handle_exceptions(flask_app)
    elif Config.SENTRY_DSN:
        from raven.contrib.flask import Sentry
        sentry = Sentry()
        sentry.init_app(flask_app, dsn=Config.SENTRY_DSN)

    flask_app.config.from_object('app.config.Config')
    flask_app.register_blueprint(app.views.blueprint_http)
    app.views.blueprint_http.config = flask_app.config

    return flask_app
