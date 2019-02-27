"""
programmatic oauth for bullhorn api
-- based on http://developer.bullhorn.com/articles/getting_started
"""
import json

from hello_settings import ENV_DICT
from hello_models.models import KeyVal
from hello_webapp.extensions import db
import urllib
try:
    from urllib import parse as urlparse
except ImportError:
     import urlparse as urlparse
import requests


def get_new_auth_code():
    base_url = 'https://auth.bullhornstaffing.com/oauth/authorize'
    qs = {
        'client_id': ENV_DICT['BULLHORN_CLIENT_ID'],
        'response_type': 'code',
        'state': ENV_DICT['BULLHORN_CONFIRM_STATE'],
        'username': ENV_DICT['BULLHORN_API_USERNAME'],
        'password': ENV_DICT['BULLHORN_API_PASSWORD'],
        'action': 'Login'
    }
    qstring = urllib.urlencode(qs)
    q_url = '{base_url}?{qstring}'.format(base_url=base_url, qstring=qstring)
    r = requests.get(q_url, allow_redirects=True)
    returned_url = r.url
    parsed_url = urlparse.urlparse(returned_url)
    parsed_qs = urlparse.parse_qs(parsed_url.query)
    auth_code = parsed_qs['code'][0]
    returned_state = parsed_qs['state'][0]
    expected_state = ENV_DICT['BULLHORN_CONFIRM_STATE']
    assert returned_state == expected_state, 'error: bullhorn returned invalid state confirmation'
    return auth_code


def get_bullhorn_tokens(save=True):

    # get auth_code
    auth_code = get_new_auth_code()

    # now get access_token using code
    base_url = 'https://auth.bullhornstaffing.com/oauth/token'
    qs = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': ENV_DICT['BULLHORN_CLIENT_ID'],
        'client_secret': ENV_DICT['BULLHORN_CLIENT_SECRET']
    }
    qstring = urllib.urlencode(qs)
    q_url = '{base_url}?{qstring}'.format(base_url=base_url, qstring=qstring)
    r = requests.post(q_url)
    returned = r.json()
    access_token = returned['access_token']
    refresh_token = returned['refresh_token']
    token_dict = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    # if save=True then cache token_dict to database
    if save:
        save_token_dict(token_dict)
    return token_dict


def get_new_session_dict(force_new_token=True):

    if not force_new_token:
        token_dict = get_saved_token_dict()
        if token_dict:
            print '++ found saved access token'
        else:
            token_dict = get_bullhorn_tokens()
    else:
        token_dict = get_bullhorn_tokens()
    print 'access_token: {}'.format(token_dict['access_token'])
    print 'refresh_token: {}'.format(token_dict['refresh_token'])

    login_url = 'https://rest.bullhornstaffing.com/rest-services/login?version=*&access_token={access_token}'.format(
        access_token=token_dict['access_token']
    )
    r = requests.get(login_url)
    print r.text
    session_dict = r.json()
    save_session_dict(session_dict)

    # return session_dict
    return session_dict


def get_session(force_new=False):
    """
    gets a session for use use with bh REST API, fetches from cache if available
    :param force_new: 
    :return: returns dictionary with keys bhRestToken and restUrl
    """
    found_saved_session = False
    if not force_new:
        session_dict = get_saved_session_dict()
        found_saved_session = session_dict is not None

    if not found_saved_session:
        print '++ fetching new session'
        session_dict = get_new_session_dict()
    else:
        print '++ found saved session'

    return session_dict


BH_TOKEN_KEY = 'bh_token'
BH_SESSION_KEY = 'bh_session'

def get_saved_token_dict():
    """
    fetches tokens from the database if they are saved
    :return: dictionary with keys access_token and refresh_token
    """
    token = db.session.query(KeyVal).filter(KeyVal.key == BH_TOKEN_KEY).one_or_none()
    if token:
        return json.loads(token.value)
    else:
        return None


def save_token_dict(token_dict):
    """
    saves token to database
    :param token_dict: dictionary with keys access_token and refresh_token
    :return: saved KeyVal object of token
    """
    token = db.session.query(KeyVal).filter(KeyVal.key == BH_TOKEN_KEY).one_or_none()
    if not token:
        token = KeyVal(key=BH_TOKEN_KEY)
    token.value = json.dumps(token_dict)
    db.session.add(token)
    db.session.commit()
    return token


def get_saved_session_dict():
    """
    fetches bh session from the database if they are saved
    :return: dictionary with keys bhRestToken and restUrl
    """
    bh_session = db.session.query(KeyVal).filter(KeyVal.key == BH_SESSION_KEY).one_or_none()
    if bh_session:
        return json.loads(bh_session.value)
    else:
        return None


def save_session_dict(session_dict):
    """
    saves session to database
    :param session_dict: dictionary with keys bhRestToken and restUrl
    :return: saved KeyVal object of token
    """
    bh_session = db.session.query(KeyVal).filter(KeyVal.key == BH_SESSION_KEY).one_or_none()
    if not bh_session:
        bh_session = KeyVal(key=BH_SESSION_KEY)
    bh_session.value = json.dumps(session_dict)
    db.session.add(bh_session)
    db.session.commit()
    return bh_session



if __name__ == '__main__':
    session_dict = get_session()
    print session_dict