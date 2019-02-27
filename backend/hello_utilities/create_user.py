import sys

from werkzeug.security import generate_password_hash

from hello_models.models import User
from hello_webapp.extensions import db


def create_user(email, password):
    print '++ creating user: {} / {}'.format(email, password)
    user = User(
        email=email,
        password=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    return user


if __name__ == '__main__':
    email = sys.argv[1]
    password = sys.argv[2]
    from hello_webapp.app import create_app
    app = create_app()
    with app.app_context():
        create_user(email, password)