import sys
import traceback

from flask import Flask, render_template

from hello_settings import BACKEND_PATH, TEMPLATE_DIR, ENV_DICT, get_db_url
from hello_utilities.log_helper import _log, _capture_exception
from hello_webapp.helper_routes import get_hello_helpers_blueprint
from hello_webapp.api.auth import get_auth_blueprint
from hello_webapp.api.bh import get_bh_blueprint
from hello_webapp.api.webhook import get_webhook_blueprint
from hello_webapp.flask_admin_routes import get_flask_admin
from hello_webapp.extensions import db, basic_auth, sentry, mail


# create flask app
def create_app():

    # log some basic things about startup and which environment we're in
    if ENV_DICT['ENVIRON'] == 'PROD':
        _log('++ USING PROD DATABASE')
    else:
        _log('++ using environ: {}'.format(ENV_DICT['ENVIRON']))

    # create the flask app
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=BACKEND_PATH)
    app.config.update(
        DEBUG=ENV_DICT.get('FLASK_DEBUG') or False,
        SECRET_KEY=ENV_DICT['FLASK_SECRET_KEY']
    )

    # initialize sql alchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
    db.init_app(app)

    # BasicAuth for flask_admin
    app.config['BASIC_AUTH_USERNAME'] = ENV_DICT['BASIC_AUTH_USERNAME']
    app.config['BASIC_AUTH_PASSWORD'] = ENV_DICT['BASIC_AUTH_PASSWORD']
    basic_auth.init_app(app)

    # initialize flask-admin
    admin = get_flask_admin()
    admin.init_app(app)

    # initialize flask-mail
    mail_keys = [
        "MAIL_SERVER",
        "MAIL_PORT",
        "MAIL_USE_TLS",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_DEFAULT_SENDER"
    ]
    for key in mail_keys:
        app.config[key] = ENV_DICT[key]
    mail.init_app(app)

    # register blueprints
    app.register_blueprint(get_hello_helpers_blueprint())
    app.register_blueprint(get_auth_blueprint())
    app.register_blueprint(get_bh_blueprint())
    app.register_blueprint(get_webhook_blueprint())

    # configure sentry
    if ENV_DICT.get('SENTRY_DSN'):
        _log('++ using Sentry for error logging')
        sentry.init_app(app, dsn=ENV_DICT['SENTRY_DSN'])

    @app.route("/api/hello/")
    def hello_page():
        return render_template("hello.html")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.errorhandler(Exception)
    def error_handler(e):
        """
        if a page throws an error, log the error to slack, and then re-raise the error
        """
        _capture_exception(e)
        # re-raise error
        raise e

    # return the app
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
