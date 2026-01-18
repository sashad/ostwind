import logging

from werkzeug.exceptions import Unauthorized

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_pbx_key(cls):
        headers = request.httprequest.environ
        pbx_key = headers.get("HTTP_PBX_KEY")
        # _logger.info(f"==== HTTP_PBX_KEY ==== {pbx_key}")
        if pbx_key:
            request.update_env(user=1)
            auth_pbx_key = request.env["ostwind.personalpbx"]._retrieve_api_key(pbx_key)
            if auth_pbx_key:
                request._env = None
                request.update_env(user=auth_pbx_key.user_id.id)
                request.pbx_device = auth_pbx_key
                return True
        _logger.error("Wrong HTTP_PBX_KEY, access denied")
        raise Unauthorized()
