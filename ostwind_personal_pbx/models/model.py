import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import consteq
from odoo.tools.translate import _

from ..lib.mobile import Status

_logger = logging.getLogger(__name__)


class PersonalPBX(models.Model):
    _name = 'x_ostwind.personalpbx'
    _description = 'Personal PBX mobile device model'
    _transient_max_days = 7

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        help="""The user of Personal PBX""",
    )

    key = fields.Char(
        required=True,
        help="""The Pbx key.""",
        index=True
    )

    available = fields.Boolean(
        readonly=False, default=False
    )

    background_mode = fields.Boolean(
        readonly=False, default=True
    )

    data = fields.Json(
        string="Data",
        help="""A call data stored in JSON format""",
    )

    result = fields.Char(
        required=False,
        help="""Returned result from a mobile device""",
    )

    status = fields.Char(
        default=Status.NONE.value,
        help="""A call status"""
    )

    data_updated = fields.Datetime(
        string="Data Updated",
        compute="_compute_data_updated",
        store=True,
        help="""The last time the data was updated""",
    )

    active = fields.Boolean(
        compute="_compute_active", readonly=False, store=True, default=True
    )

    @api.depends(
        "user_id.active"
    )
    def _compute_active(self):
        for record in self:
            record.active = record.user_id.active

    @api.depends('data', 'status')
    def _compute_data_updated(self):
        for record in self:
            if (record.data and record.data != record._origin.data) \
                    or (record.status != record._origin.status):
                record.data_updated = fields.Datetime.now()

    @api.model
    def _retrieve_api_key(self, key):
        return self.browse(self._retrieve_api_key_id(key))

    @api.model
    def _retrieve_api_key_id(self, key):
        for api_key in self.search([]):
            if api_key.key and consteq(key, api_key.key):
                return api_key.id
        raise ValidationError(_("The key %s is not allowed") % key)

    @api.model
    def is_available(self):
        """ Check the pbx is available. """
        current_user = self.env.user
        record = self.search([('user_id', '=', current_user.id)], limit=1)
        return record and record.available

    @api.model
    def partner_call(self, *args, **kwargs):
        """ action on a partner select field phone click. """
        current_user = self.env.user
        record = self.search([('user_id', '=', current_user.id)], limit=1)
        _logger.info(f"=== {args=} {kwargs=}")
        if not record or not record.available:
            return {
                "success": False,
                "message": 'Your mobile application is not run.'
                           ' Run the app and try again.'
                }
        if record.background_mode:
            return {
                "success": False,
                "message": 'Your mobile application is background.'
                           ' Activate the app and try again.'
                }
        # clear the phone string from any symbole except "+" and digits
        phone = args[0]
        success = not record.status or record.status in [
                Status.NONE.value,
                Status.REJECTED.value,
                Status.DONE.value
            ]
        if success:
            data = kwargs or {}
            data["user_id"] = record.user_id.id
            data["record_id"] = record.id
            data["res_model"] = args[1]
            data["res_id"] = args[2]
            record.write({
                'status': Status.CREATED.value,
                'data': {phone: data}
            })
            return {"success": success, "data": {phone: data}}
        else:
            return {
                "success": success,
                "message": 'Your mobile application is busy.'
            }

    @api.model
    def set_call_status(self, status):
        """ set a current call status. """
        current_user = self.env.user
        record = self.search([('user_id', '=', current_user.id)], limit=1)
        record.write({
            'status': status
        })
        return {"success": True}
