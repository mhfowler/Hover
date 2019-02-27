from functools import wraps
import re

from flask import request, jsonify, make_response

from hello_models.models import User
from hello_webapp.extensions import db
from hello_utilities.token_helper import token_decode
from hello_utilities.log_helper import _log
from hello_settings import ENV_DICT


def get_user_from_header():
    """
    Gets the User object of currently logged in user from the X-ACCESS-TOKEN in the header
    :return: None
    """
    token = request.headers.get('X-ACCESS-TOKEN', None)
    decode_response = token_decode(token)
    if not decode_response['success']:
        return None
    payload = decode_response['payload']
    user_id = payload['user_id']
    current_user = db.session.query(User).filter(
        User.user_id == user_id,
    ).one_or_none()
    return current_user


def authentication_required(f):
    """
    wrapper for flask routes which makes them require authentication
    :param f: flask view to be wrapped
    :return: returns flask view which requires authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_user_from_header()
        if not current_user:
            response = jsonify({
                'success': False,
                'message': 'Not Authorized: invalid token'
            })
            response.status_code = 403
            return response

        # pass current_user to route function
        kwargs['current_user'] = current_user

        return make_response(f(*args, **kwargs))
    return decorated_function