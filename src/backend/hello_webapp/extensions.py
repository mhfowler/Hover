"""
initializes extensions which are then configured in create_app()
based on the Flask factory pattern (http://flask.pocoo.org/docs/0.12/patterns/appfactories/)
"""
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from raven.contrib.flask import Sentry

# for sending emails
mail = Mail()

# sqlalchemy
db = SQLAlchemy()

# flask-BasicAuth for flask-admin
basic_auth = BasicAuth()

# sentry
sentry = Sentry()