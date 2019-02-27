import re

from flask import request, jsonify, Blueprint

from hello_utilities.bullhorn.bullhorn_api import BullhornApi
from hello_utilities.log_helper import _log, _capture_exception
from hello_utilities.send_email import send_email
from hello_settings import TEMPLATE_DIR, ENV_DICT


def truncate_email(email_content):
    """
    helper function which strips email_content down to just the actual message sent
    (not including replies and other things)
    :param email_content: string contents of email
    :return: truncated string contents of email
    """
    # first try removing any
    lines = email_content.split('\n')
    keep_lines = []
    found_reply = False
    for index in range(0, len(lines)):
        line = lines[index]
        m = re.match('>> On.*at.* wrote:', line)
        if m:
            test_line = lines[index + 2]
            if test_line.startswith('>>>'):
                _log('++ truncating email at line "{}"'.format(line))
                keep_lines.append(line)
                keep_lines.append('... truncated')
                found_reply = True
                break

        # if we made it here, then just keep going
        keep_lines.append(line)

    # combine keep_lines
    to_return = '\n'.join(keep_lines)

    # if we didn't already truncate, then just truncate to first 3000 characters
    if not found_reply:
        if len(to_return) > 3000:
            to_return = to_return[:3000]
            to_return += '.... truncated after 3000 char'

    # return whatever we have
    return to_return


def get_webhook_blueprint():
    # blueprint for these routes
    webhook_blueprint = Blueprint('webhook_blueprint', __name__, template_folder=TEMPLATE_DIR)

    @webhook_blueprint.route('/api/email/webhook/', methods=['POST', 'GET'])
    def api_email_webhook(**kwargs):
        """
        endpoint to post emails to (via zapier integration)
        """
        api_key = request.headers.get('CPI-API-KEY', None)
        if not api_key == ENV_DICT['CPI_API_KEY']:
            raise Exception('++ email webhook with bad api key')

        # should we save the date of last-response
        # whether this key is set in the header or not is configured within zapier for a particular email address
        save_last_response = request.headers.get('LAST-RESPONSE', None) == '1'

        data = request.form
        to_email = data['raw__To_email']
        # recipient_email = data['recipient'] ## this just contains the bcc
        from_email = data['from_email']
        email_content = data['body_plain']
        subject = data['subject']

        # truncate the email (to avoid replies showing up as part of the email content)
        note_content = truncate_email(email_content)

        # log message
        _log('++ received web hook with data. to_email: {to_email} | subject: {subject} | save_last_response: {save_last_response}'.format(
            to_email=to_email,
            subject=subject,
            save_last_response=save_last_response,
        ))

        # attempt to create note
        bapi = BullhornApi()

        # create the note
        search_results = bapi.search_candidates(input=to_email, fields='email,id,firstName,lastName')
        error_msg = None
        if search_results:
            candidate = search_results[0]
            if candidate['email'] == to_email:

                # if save_last_response, then update the save_last_response field of this candidate
                if save_last_response:
                    try:
                        bapi.save_last_response(candidate['id'])
                    except:
                        _log('++ failed to update last_response_date for {}'.format(to_email))

                # then also create the note for this user
                note_id = bapi.create_note(
                    comments=note_content,
                    action='Email sent',
                    candidate_id=candidate['id'],
                    author_email=from_email,
                )
                _log('++ created note via email: {}'.format(note_id))
                if note_id:
                    response = jsonify({
                        'success': 'True',
                        'message': 'created note'
                    })
                    response.status_code = 200
                    return response
                else:
                    error_msg = 'Failed to create note for candidate'.format(to_email)
            else:
                error_msg = 'Search found candidate with non-matching email {}'.format(candidate['email'])
        else:
            error_msg = 'Failed to find candidate in bullhorn with email'.format(to_email)

        # if we reached here, then a note was not created, and we should send an error email
        _log('++ note creation failure for email sent to {}. With error: {}'.format(to_email, error_msg))
        alert_email_set = set(ENV_DICT['ALERT_EMAILS'])
        alert_email_set.add(from_email)
        for alert_email in alert_email_set:
            t_vars = {
                'email_content': email_content,
                'to_email': to_email,
                'subject': subject,
                'error_msg': error_msg,
            }
            send_email(
                to_email=alert_email,
                subject='Note Creation Failure',
                template_path='emails/alert_email.html',
                template_vars=t_vars
            )
        response = jsonify({
            'success': 'False',
            'message': 'failed to created note'
        })
        response.status_code = 200
        return response

    # finally return blueprint
    return webhook_blueprint