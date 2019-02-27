"""
this file contains helper routes which are not essential to the app
but are useful for debugging server configurations
"""
from flask import Blueprint
from flask import jsonify
from flask import render_template

from hello_settings import TEMPLATE_DIR, ENV_DICT
from hello_utilities.log_helper import _log
from hello_utilities.create_test_object import get_test_objects, create_test_object
from hello_utilities.send_email import send_test_email
from hello_webapp.extensions import db


def get_hello_helpers_blueprint():

    # blueprint for these routes
    hello_helpers = Blueprint('hello_helpers', __name__, template_folder=TEMPLATE_DIR)

    @hello_helpers.route('/api/error/')
    def flask_force_error():
        """
        this helper page forces an error, for testing error logging
        """
        raise Exception('forced 500 error')

    @hello_helpers.route('/api/slack/')
    def flask_slack_test():
        """
        this helper page for testing if slack is working
        """
        _log('@channel: slack is working?')
        return 'slack test'

    @hello_helpers.route('/api/email/')
    def flask_email_test():
        """
        this helper page for testing if email sending is working
        """
        _log('++ sending test email')
        send_test_email(ENV_DICT['MAIL_DEFAULT_SENDER'])
        return 'email test'

    @hello_helpers.route('/api/test_db/')
    def test_db_page():
        """
        this helper page confirms that the database is connected and working
        :return:
        """
        create_test_object(db.session)
        test_objects = get_test_objects(db.session)
        return render_template("hello_db.html", test_objects=test_objects)

    @hello_helpers.route('/api/test/')
    def test_endpoint():
        """
        this helper page helps test that the front-end is communicating to the backend
        :return:
        """
        return jsonify({
            'message': 'hello endpoint'
        })

    # finally return blueprint
    return hello_helpers

