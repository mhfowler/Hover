from flask_mail import Message
from flask import render_template

from hello_utilities.log_helper import _log
from hello_webapp.extensions import mail
from hello_settings import ENV_DICT


def send_email(to_email, subject, template_path, template_vars):

    # email address that emails will be sent from
    from_email = ENV_DICT['MAIL_DEFAULT_SENDER']

    # render HTML from template
    page_html = render_template(template_path, **template_vars)

    msg = Message(subject=subject,
                  sender=from_email,
                  recipients=[to_email],
                  html=page_html)
    mail.send(msg)


def send_test_email(to_email):
    t_vars = {
        'first_name': 'Test',
        'last_name': 'User'
    }
    send_email(to_email=to_email,
               subject='Hello',
               template_path='emails/test_email.html',
               template_vars=t_vars)


if __name__ == '__main__':
    from hello_webapp.app import create_app
    app = create_app()
    with app.app_context():
        send_test_email('cpi.search.bot@gmail.com')