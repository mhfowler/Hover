import json

from flask import request, jsonify, Blueprint

from hello_utilities.bullhorn.bullhorn_api import BullhornApi
from hello_utilities.auth_helper import authentication_required
from hello_utilities.log_helper import _log, _capture_exception
from hello_settings import TEMPLATE_DIR


def get_bh_blueprint():
    # blueprint for these routes
    bh_blueprint = Blueprint('bh_blueprint', __name__, template_folder=TEMPLATE_DIR)

    @bh_blueprint.route('/api/search/candidates/', methods=['POST'])
    @authentication_required
    def api_search_candidates(**kwargs):
        """
        endpoint to search for candidates in bullhorn with the given string
        """
        data = json.loads(request.data) if request.data else {}
        bapi = BullhornApi()

        query = data['query'].strip()
        candidates = bapi.fast_find_candidates(query)

        response = jsonify({
            'candidates': candidates,
        })
        response.status_code = 200
        return response

    @bh_blueprint.route('/api/comment-actions/', methods=['GET'])
    @authentication_required
    def api_get_comment_actions(**kwargs):
        """
        endpoint to get allowed comment action strings
        """
        bapi = BullhornApi()
        actions = bapi.get_comment_action_list()
        response = jsonify({
            'actions': actions,
        })
        response.status_code = 200
        return response

    @bh_blueprint.route('/api/note/', methods=['POST'])
    @authentication_required
    def api_create_note(**kwargs):
        data = json.loads(request.data) if request.data else {}
        bapi = BullhornApi()

        action = data['action']
        comments = data['comments']
        candidate_id = data['candidateId']
        try:
            note_id = bapi.create_note(action=action, comments=comments, candidate_id=candidate_id)
            if note_id:
                _log('++ created note: {}'.format(note_id))
                to_return = {
                    'success': True,
                    'note_id': note_id,
                }
            else:
                to_return = {
                    'success': False,
                    'message': 'API error'
                }
        except Exception as e:
            _capture_exception(e)
            to_return = {
                    'success': False,
                    'message': 'API error'
            }

        response = jsonify(to_return)
        response.status_code = 200
        return response


    # finally return blueprint
    return bh_blueprint