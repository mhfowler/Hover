"""
utils for querying bullhorn api
"""
import json
import urllib
import requests
import time

from hello_utilities.bullhorn.bullhorn_tokens import get_session
from hello_utilities.log_helper import _log


class BullhornApi():

    def __init__(self):
        # initialize the session with tokens needed for querying
        self.session = get_session()
        self.retries = 0

    def req(self, endpoint, args, method='GET'):

        # construct base url
        base_url = '{base}{endpoint}'.format(
                endpoint=endpoint,
                base=self.session['restUrl']
        )

        if method == 'GET':
            # construct the URL to make the request to
            # add the rest token to the query string
            args['BhRestToken'] = self.session['BhRestToken']
            qstring = urllib.urlencode(args)
            url = '{base_url}?{qstring}'.format(
                base_url=base_url,
                qstring=qstring
            )
            print url
            r = requests.get(url)
        elif method == 'PUT':
            qstring_args = {'BhRestToken': self.session['BhRestToken']}
            qstring = urllib.urlencode(qstring_args)
            url = '{base_url}?{qstring}'.format(
                base_url=base_url,
                qstring=qstring
            )
            r = requests.put(url, json=args)
        elif method == 'POST':
            qstring_args = {'BhRestToken': self.session['BhRestToken']}
            qstring = urllib.urlencode(qstring_args)
            url = '{base_url}?{qstring}'.format(
                base_url=base_url,
                qstring=qstring
            )
            r = requests.post(url, json=args)
        else:
            raise Exception('++ not yet implemented')

        # parse to json and return
        returned = r.json()

        # check for error codes
        if returned.get('errorCode') and returned.get('errorCode') == 401:
            self.session = get_session(force_new=True)
            self.retries += 1
            if self.retries > 3:
                raise Exception('++ tried three times with no success for call {} {} {}'.format(endpoint, args, method))
            else:
                return self.req(endpoint, args, method)

        return returned

    def get_notes(self):
        return self.req('allCorpNotes', {'count':5, 'start':0, 'fields':'*'})

    def get_entity(self, entity_name, entity_id, args):
        """
        Use the following syntax to filter the to - many entities that are returned in a response.
        All three parts of the syntax are optional.The where - filter is delimited by curly braces.
        fields = fieldName[count](sub - fields) {where - filter}
        """
        endpoint = 'entity/{}/{}'.format(entity_name, entity_id)
        returned = self.req(endpoint=endpoint, args=args)
        return returned

    def update_entity(self, entity_name, entity_id, args):
        """
        POST request is used to update entity (this is the strangest oddity of the BH api)
        :param entity_name: string name of entity
        :param args: dictionary of args
        :param entity_id: bullhorn string of entity to update
        :return: whatever is returned by bh
        """
        endpoint = 'entity/{}/{}'.format(entity_name, entity_id)
        returned = self.req(endpoint=endpoint, args=args, method='POST')
        return returned

    def create_entity(self, entity_name, args):
        endpoint = 'entity/{}'.format(entity_name)
        returned = self.req(endpoint=endpoint, args=args, method='PUT')
        return returned

    def get_comment_action_list(self):
        endpoint = 'settings/commentActionList'
        returned = self.req(endpoint, {})
        return returned['commentActionList']

    def get_candidate(self, candidate_id, args=None):
        if not args:
            args = {
                'fields': 'firstName,lastName,address,notes'
            }
        returned = self.get_entity('Candidate', candidate_id, args)
        return returned['data']

    def get_note(self, note_id, args=None):
        if not args:
            args = {
                'fields': '*'
            }
        returned = self.get_entity('Note', note_id, args)
        return returned

    def get_ten_recent_candidate_notes(self, candidate_id):
        args = {
            'fields': 'firstName,lastName,address,notes[10]'
        }
        candidate = self.get_candidate(candidate_id=candidate_id, args=args)
        note_ids = candidate['notes']['data']
        print note_ids
        notes = []
        total_notes = candidate['notes']['total']
        for note_id in note_ids:
            print '++ fetching note: {}'.format(note_id)
            note = self.get_note(note_id['id'])
            notes.append(note['data'])
        notes.sort(key=lambda n: n['dateAdded'], reverse=True)
        return notes

    def get_all_candidate_notes(self, candidate_id):
        """
        the maximum number of notes this returns is 500, if a candidate has more than 500 notes
        some type of pagination will be necessary. See: http://supportforums.bullhorn.com/viewtopic.php?f=104&t=23776
        :param candidate_id: id of candidate to fetch notes for
        :return: list of Note dictionaries
        """
        endpoint = 'query/NoteEntity'
        args = {
            'fields': 'note(*)',
            'where': 'targetEntityID={}'.format(candidate_id),
            'count': 500
        }
        returned = self.req(endpoint=endpoint, args=args)
        notes = returned['data']
        notes.sort(key=lambda n: n['note']['dateAdded'], reverse=True)
        return notes

    def get_all_candidates(self):
        """
        the maximum number of notes this returns is 500, if a candidate has more than 500 notes
        some type of pagination will be necessary. See: http://supportforums.bullhorn.com/viewtopic.php?f=104&t=23776
        :param candidate_id: id of candidate to fetch notes for
        :return: list of Note dictionaries
        """
        endpoint = 'search/Candidate'
        args = {
            'fields': 'firstName,lastName',
            'showTotalMatched': True,
            'count': 500,
            'query': 'firstName:M'
        }
        keep_searching = True
        candidates = []
        num_found = 0
        while keep_searching:
            returned = self.req(endpoint=endpoint, args=args)
            candidates.extend(returned['data'])
            if not len(returned):
                keep_searching = False
            num_found += len(returned)
            args['start'] = num_found
        # return candidates
        return candidates

    def save_last_response(self, candidate_id):
        """
        updates the last_response_date field for the given candidate to the current time
        :param candidate_id: string bullhorn id of candidate to update
        :return:
        """
        args = {
            'customDate3': int(time.time()) * 1000  # in java, times are measured in ms not seconds
        }
        # and update/put this candidate
        returned = self.update_entity(entity_name='Candidate', entity_id=candidate_id, args=args)
        return returned

    def search_candidates(self, input, fields='*'):
        """

        :return:
        """
        if '@' in input:
            query = 'email:{}'.format(input)
        else:
            query = 'name:"{}"'.format(input)
        endpoint = 'search/Candidate'
        args = {
            'fields': fields,
            'showTotalMatched': True,
            'count': 5,
            'query': query
        }
        returned = self.req(endpoint=endpoint, args=args)
        candidates = []
        candidates.extend(returned['data'])
        # return candidates
        return candidates

    def query_corporate_user(self, username):
        """
        returns all users of bullhorn
        :return: list of users
        """
        endpoint = 'query/CorporateUser'
        args = {
            'fields': '*',
            'orderBy': 'username',
            'count': '500',
            'start': '0',
            'where': "email='{}'".format(username)
        }
        returned = self.req(endpoint=endpoint, args=args)
        return returned['data']

    def get_all_corporate_user(self):
        """
        returns all users of bullhorn (who are enabled to login)
        :return: list of users
        """
        endpoint = 'query/CorporateUser'
        args = {
            'fields': '*',
            'orderBy': 'username',
            'count': '500',
            'start': '0',
            'where': "enabled=true"
        }
        returned = self.req(endpoint=endpoint, args=args)
        return returned['data']

    def fast_find_candidates(self, query):
        """
        uses bullhorn fast-find for search
        and filter down to just candidates
        :return:
        """
        endpoint = 'find'
        args = {
            'query': query,
            'countPerEntity': 5
        }
        returned = self.req(endpoint=endpoint, args=args)
        candidates = filter(lambda e: e.get('entityType') == 'Candidate', returned['data'])
        # look up more info for candidates
        to_return = []
        for candidate in candidates:
            args = {
                'fields': 'firstName,lastName,companyName,email'
            }
            c = self.get_entity(entity_name='Candidate', entity_id=candidate['entityId'], args=args)
            if c.get('data'):
                c = c['data']
                c['entityId'] = candidate['entityId']
                title = '{firstName} {lastName}'.format(
                    firstName=c['firstName'],
                    lastName=c['lastName'],
                )
                if c.get('email'):
                    title += ' ({})'.format(c['email'])
                if c.get('companyName'):
                    title += ' | {}'.format(c['companyName'])
                c['title'] = title
                to_return.append(c)
            else:
                print '++ error: {}'.format(c)
        return to_return

    def create_note(self, comments, action, candidate_id, author_email=None):
        """
        creates a note with inputted fields
        :param comments: text of the note
        :param action: coded string of type of note
        :param candidate_id: string bullhorn id of the candidate the note should be added to
        :param author_email: string email address of the recruiter that should be listed as the author
        :return: note object
        """
        note_args = {
            'action': action,
            'comments': comments,
            'personReference': {
                '_subtype': 'Candidate',
                'id': candidate_id
            }
        }
        if author_email:
            corp_users = self.query_corporate_user(author_email)
            if corp_users:
                corp_user = corp_users[0]
                note_args['commentingPerson'] = {
                    '_subtype': 'CorporateUser',
                    'id': corp_user['id']
                }
            else:
                _log('++ failed to find corporate user with email: {}'.format(author_email))

        returned = self.create_entity('Note', note_args)
        if returned['changeType'] == 'INSERT':
            return returned['changedEntityId']
        else:
            raise Exception('++ failed to create note: {}'.format(json.dumps(returned)))


if __name__ == '__main__':
    from hello_webapp.app import create_app
    app = create_app()
    with app.app_context():
        bapi = BullhornApi()

        test_id = 59632
        test_id2 = 95576
        # bapi.get_candidate(test_id)
        # bapi.get_candidate_notes(test_id)
        # notes = bapi.query_notes(test_id)
        # candidates = bapi.get_all_candidates()
        # candidates = bapi.search_candidates('Max Fowl')
        # candidates = bapi.search_candidates('maxhfowler@gmail.com')
        # candidates = bapi.fast_find_candidates('sonyakc.2007@gmail.com')
        # # # print len(candidates)
        # for c in candidates:
        #     print c['entityId']
        #     print c['title']
        # #
        # notes = bapi.get_all_candidate_notes(test_id)

        # users = bapi.get_all_corporate_user()
        # for u in users:
        #     print 'username: {}'.format(u['username'])
        #     print 'email: {}'.format(u['email'])
        #     print 'id: {}'.format(u['id'])
        #     print '***********'

        # u = bapi.query_corporate_user('jkeenan@cpi-search.com')
        # # u = bapi.query_corporate_user('test')
        # print u

        #
        # note_args = {
        #     'action': 'Left Message',
        #     'comments': 'this is a test message 1',
        #     'personReference': {
        #         '_subtype': 'Candidate',
        #         'id': test_id
        #     }
        # }

        # bapi.create_entity('Note', note_args)

        # c = bapi.get_candidate(candidate_id=test_id2, args={'fields': '*'})
        # print c

        bapi.save_last_response(candidate_id=test_id)
        #
        # note_id = bapi.create_note(
        #     action='Left Message',
        #     comments='this is a test note with author',
        #     candidate_id=test_id,
        #     author_email='jkeenan@cpi-search.com'
        # )
        # print ('++ created note: {}'.format(note_id))