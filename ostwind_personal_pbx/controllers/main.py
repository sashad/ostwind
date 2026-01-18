import json
import logging
import time

from odoo import http
from odoo.http import Response, request

from odoo.addons.web.controllers.session import Session

from ..lib.mobile import Status

_logger = logging.getLogger(__name__)

SMS_STATE_OUTGOING = 'outgoing'
SMS_STATE_ERROR = 'error'
SMS_STATE_PROCESS = 'process'
SMS_STATE_SENT = 'sent'
SMS_FAILURE_TYPE_ACC = 'sms_acc'
SMS_FAILURE_TYPE_NOT_DELIVERED = 'sms_not_delivered'
SMS_NOTIFICATION_STATUS_EXCEPTION = 'exception'


class IndexPage(http.Controller):
    @http.route(
        '/personal_pbx',
        auth='none',
        website=False,
        csrf=False,
        cors='*'
    )
    def my_custom_page(self, db=None, **kw):
        return request.render(
            'ostwind_personal_pbx.index_page_template'
        )


class LongPollingController(http.Controller):

    def isAuthorized(self):
        # Get the API key from the Authorization header
        auth_header = request.httprequest.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        # Extract the API key
        api_key = auth_header.split(' ')[1]
        session_id = request.session.sid
        if session_id != api_key:
            return None
        user = self.getUser(api_key)
        if not user:
            return None

        return user

    @http.route(
        '/api/ostwind/personal_pbx/longpoll',
        type='http',
        auth='pbx_key',
        methods=['GET', 'POST', 'OPTIONS'],
        csrf=False,
        cors='*'
    )
    def longpoll(self, db=None, last_sms_id=None, **kwargs):
        """ Long poll method """
        timeout = 30  # Timeout in seconds
        start_time = time.time()

        request.pbx_device.write({
            'available': True
        })
        while time.time() - start_time < timeout:
            record = request.env['ostwind.personalpbx'].browse(
                request.pbx_device.id
            )
            if record and record.status == Status.CREATED.value:
                result = {
                    "status": "call",
                    "data": record.data
                }
                # record.write({})
                request.pbx_device.write({
                    'status': Status.PROCESS.value
                })
                return Response(
                    json.dumps(result),
                    content_type='application/json',
                    status=200
                )
            elif not record.status or record.status in [
                        Status.NONE.value,
                        Status.REJECTED.value,
                        Status.DONE.value
                    ]:
                # Here selection of a sms.
                request.env.cr.execute(
                    """
                        SELECT sms.id
                        FROM mail_message mail
                        INNER JOIN sms_sms sms
                            ON sms.mail_message_id = mail.id
                        WHERE
                            mail.author_id = %s
                            AND
                            sms.state = %s
                        LIMIT 1;
                    """,
                    (
                        request.pbx_device.user_id.partner_id.id,
                        SMS_STATE_PROCESS
                    )
                )
                sms_in_process = request.env.cr.fetchone()
                if sms_in_process:
                    sms_id = sms_in_process[0]
                    sms = request.env['sms.sms'].browse(sms_id)
                    result = {
                        "status": "sms",
                        "data": {
                            "phone": sms.number,
                            "message": sms.body,
                            "smsId": sms.id,
                        }
                    }
                    if int(last_sms_id) != sms_id:
                        return Response(
                            json.dumps(result),
                            content_type='application/json',
                            status=200
                        )
                else:
                    query = """
                        SELECT
                            mail.id AS mail_id,
                            sms.id AS sms_id,
                            notify.id AS notification_id,
                            sms.failure_type,
                            sms.state,
                            sms.uuid
                        FROM mail_message mail
                        INNER JOIN sms_sms sms
                            ON sms.mail_message_id = mail.id
                        INNER JOIN mail_notification notify
                            ON notify.mail_message_id = mail.id
                        WHERE
                                mail.message_type = 'sms'
                            AND
                                mail.author_id = %s
                            AND
                                (
                                    sms.state = %s
                                    OR
                                    (
                                        sms.state = %s
                                        AND
                                        sms.failure_type = %s
                                    )
                                )
                        ORDER BY mail.id
                        LIMIT 1;
                    """
                    params = (
                        request.pbx_device.user_id.partner_id.id,
                        SMS_STATE_OUTGOING,
                        SMS_STATE_ERROR,
                        SMS_FAILURE_TYPE_ACC
                    )
                    request.env.cr.execute(query, params)
                    sms_raw = request.env.cr.dictfetchone()
                    if sms_raw:
                        sms = request.env['sms.sms'].browse(
                            sms_raw["sms_id"]
                        )
                        sms.write({
                            "state": SMS_STATE_PROCESS,
                            "failure_type": None,
                        })

            try:
                request.env.cr.commit()
            finally:
                pass

            time.sleep(1)  # Sleep to avoid busy waiting

        result = {
            "status": "timeout",
            "message": "No updates received within the timeout period"
        }
        return Response(
            json.dumps(result),
            content_type='application/json',
            status=200
        )

    @http.route(
        '/api/ostwind/personal_pbx/send_data',
        type='http',
        auth='pbx_key',
        methods=['POST'],
        csrf=False,
        cors='*'
    )
    def send_data(self, db=None, **kwargs):
        data = request.httprequest.get_json()

        if kwargs.get('action') == 'status':
            request.pbx_device.write({
                'background_mode': data.get('isBackgroundMode')
            })

        elif kwargs.get('action') == 'set_call_status':
            request.pbx_device.write({
                'status': data.get("status")
            })

        elif kwargs.get('action') == 'set_sms_state':
            sms = request.env['sms.sms'].browse(data.get('smsId'))
            notification = request.env['mail.notification'].search([(
                'mail_message_id',
                '=',
                sms.mail_message_id.id
            )])
            notification.sudo().write({
                'notification_status': data.get("notification_status"),
                'failure_type': data.get("failure_type"),
            })
            sms.write({
                'state': data.get("state")
            })

        elif kwargs.get('action') == 'response':
            if data.get('action') == 'call':
                # Log the call as a "Log note" record
                self._response_call(data)
            elif data.get('action') == 'sms':
                self._response_sms(data)

        return Response(
            json.dumps({'result': 'OK'}),
            content_type='application/json',
            status=200
        )

    def _response_call(self, data):
        if request.pbx_device.data:
            request.pbx_device.write({
                'status': Status.DONE.value,
                'result': data.get('error') or 'success'
            })
            for phone, call_data in request.pbx_device.data.items():
                if call_data.get('res_model') and call_data.get('res_id'):
                    color = 'green'
                    if data.get('error'):
                        color = 'red'
                    request.env['mail.message'].create({
                        'model': call_data.get('res_model'),
                        'res_id': call_data.get('res_id'),
                        'body': f"Call to <b>{phone}"
                                f" {call_data.get('name', '')}</b>."
                                f'<br/><span style="color: {color}">'
                                f'Result: {request.pbx_device.result}'
                                f'</span>',
                        'message_type': 'notification',
                        'subtype_id': request.env.ref('mail.mt_note').id,
                        'author_id': request.pbx_device.user_id.partner_id.id,
                    })
                    request.env['bus.bus']._sendone(
                        'pbx_res_pertner',
                        'LOG_REFRESH',
                        {
                            'message': 'record_updated',
                            'id': call_data.get('res_id')
                        }
                    )

    def _response_sms(self, data):
        sms = request.env['sms.sms'].browse(data.get('smsId'))
        notification = request.env['mail.notification'].search([(
            'mail_message_id',
            '=',
            sms.mail_message_id.id
        )])
        if data.get('success'):
            notification.sudo().write({
                'notification_status': SMS_STATE_SENT,
                'failure_type': None,
                'failure_reason': None,
            })
            sms.write({
                'state': SMS_STATE_SENT
            })
        else:
            notification.sudo().write({
                'notification_status': SMS_NOTIFICATION_STATUS_EXCEPTION,
                'failure_type': SMS_FAILURE_TYPE_NOT_DELIVERED,
                'failure_reason': data.get('error'),
            })
            sms.write({
                'state': 'error'
            })


class PbxSession(Session):
    @http.route(
        '/web/session/authenticate',
        type='json',
        auth="none",
        methods=['POST'],
        csrf=False,
        cors='*',
        save_session=True
    )
    def authenticate(self, db, login, password, **kw):
        parent_result = super().authenticate(
            db,
            login,
            password,
            **kw
        )

        request.future_response.set_cookie(
            'session_id', request.session.sid,
            max_age=http.SESSION_LIFETIME, httponly=False,
            secure=True, samesite="None"
        )
        parent_result['session_id'] = request.session.sid

        device_record = request.env['ostwind.personalpbx'].search(
            [('user_id', '=', parent_result['uid'])], limit=1)
        if device_record:
            device_record.write({
                'available': True,
                'background_mode': False,
                'status': Status.NONE.value,
                'key': request.session.sid
            })
        else:
            request.env['ostwind.personalpbx'].create({
                'user_id': parent_result['uid'],
                'key': request.session.sid,
                'available': True
            })

        return parent_result
