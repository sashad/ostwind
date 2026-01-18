from odoo import models

# import logging

# _logger = logging.getLogger(__name__)


class PbxSms(models.Model):
    # _name = 'ostwind.personalpbx.sms'
    _inherit = 'sms.sms'

    def _send(self, *args, **kwargs):
        """ Override to block sending the original actions. """

        current_user = self.env.user
        record = self.env['x_ostwind.personalpbx'].search(
            [('user_id', '=', current_user.id)],
            limit=1
        )
        message = None
        if not record or not record.available:
            message = """Your mobile application is not run.
                         Run the app and try again."""
        elif record.background_mode:
            message = """Your mobile application is background.
                         Activate the app and try again."""

        if message:
            # Send a notification to a specific user
            self.env['bus.bus']._sendone(
                'pbx_res_pertner',
                'PBX_NOTIFY',
                {
                    'message': message
                }
            )
        # messages = [{
        #     'content': body,
        #     'numbers': [{
        #         'number': sms.number,
        #         'uuid': sms.uuid
        #     } for sms in body_sms_records],
        # } for body, body_sms_records in self.grouped('body').items()]

        # _logger.info(
        #     f'++++++ _send ++++++ {messages=} {kwargs=} {self.env.context}'
        # )
