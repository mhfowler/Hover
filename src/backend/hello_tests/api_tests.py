import unittest
import json

from flask import current_app

from hello_models.database import init_db
from hello_settings import ENV_DICT
from hello_utilities.create_user import create_user
from hello_webapp.extensions import db

TEST_TENANCY = 'test'

def create_test_data():
    """
    deletes all data in database, and recreates test data
    for the purpose of testing
    """
    if 'prod' in ENV_DICT['DB_CONNECTION']['database']:
        raise Exception('++ cannot create test data in production database')

    print '++ CURRENT DB_CONNECTION: {}'.format(ENV_DICT['DB_CONNECTION']['database'])
    db.session.rollback()
    require_confirmation = True
    if require_confirmation:
        choice = raw_input('Are you sure you want to delete all data in this database? Type confirm then enter to confirm: \n')
        if not choice == 'confirm':
            raise Exception('++ aborting')
    print '++ deleting data in database and creating test data'
    print '++ deleting users'
    db.session.execute('delete from "users"')

    # creating data
    create_user('test@gmail.com', 'test')


class FlaskrTestCase(unittest.TestCase):
    """
    Unit tests must be run within a Flask application context (to get access to the database)
    see app.app_context() at the bottom of this file
    (and read documentation here: http://flask.pocoo.org/docs/0.12/appcontext/)
    """

    def setUp(self):

        # confirm the environment of the app is in TEST mode, and raise exception if not
        if ENV_DICT['ENVIRON'] != 'TEST':
            raise Exception('Error: cannot run tests not in test mode')

        # change the current_app config to be in test mode
        self.application = current_app
        self.application.config['TESTING'] = True
        self.client = self.application.test_client()

        # create tables in the database
        # NOTE: if there is a hanging connection to the database, this drop command may hang
        # you can either kill all connections to the database (or re-start your computer)
        # or change this boolean to False
        CREATE_TABLES = True
        if CREATE_TABLES:
            print '++ creating all tables'
            init_db()

        # create test data
        print '++ creating test data'
        create_test_data()

        # user login and save token to self.token
        rv = self.client.post('/api/auth/', data=json.dumps({
            'email': 'test@gmail.com',
            'password': 'test',
            'auth_type': 'email',
        }), content_type = 'application/json')
        data = json.loads(rv.data)
        assert data['token'] is not None
        self.token = data['token']

    def put_helper(self, url, data):
        """
        helper which sends an authenticated put request
        :param url: string of url to send request to
        :param data: data to pass as paramst to request
        :return: returns result of request
        """
        return self.client.put(url, data=json.dumps(data), headers={'X-ACCESS-TOKEN': self.token})

    def get_helper(self, url):
        """
        helper which sends an authenticated get request
        :param url: string of url to send request to
        :return: returns result of request
        """
        return self.client.get(url, headers={'X-ACCESS-TOKEN': self.token})

    def del_helper(self, url):
        """
        helper which sends an authenticate delete request
        :param url: string of url to send request to
        :return: returns result of request
        """
        return self.client.delete(url, headers={'X-ACCESS-TOKEN': self.token})

    def tearDown(self):
        print '++ tearDown tests'

    def test_test_is_working(self):
        rv = self.client.get('/api/test/')
        data = json.loads(rv.data)
        assert data['message'] == 'hello endpoint'


if __name__ == '__main__':
    from hello_webapp.app import create_app
    app = create_app()
    with app.app_context():
        unittest.main()