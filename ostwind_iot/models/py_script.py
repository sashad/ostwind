import json

# import logging
from odoo import SUPERUSER_ID, api, fields, models
from odoo.tools import ormcache

from .restricted import safe_eval

# _logger = logging.getLogger(__name__)

# class ResConfigSettings(models.TransientModel):
#     """Restricted Python Script Setting"""
#     _inherit = 'res.config.settings'
#     _description = "Restricted Python Script Setting"

#     allowed_modules = fields.Char(
#         string="Allowed Modules for Restricted Python Scripts",
#         config_parameter='restricted_py_script.allowed_modules',
#     )


class PyScript(models.Model):
    _name = "py.script"
    _description = "Restricted Python Scripts"

    name = fields.Char(required=True)
    # Used for calling from a script
    key = fields.Char(required=True, unique=True, help="An Unique String")
    default_context = fields.Json(help="Any JSON structure")
    code = fields.Text()
    active = fields.Boolean(default=True)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user
    )
    result_id = fields.Many2one(
        'py.script.result',
        string="Result",
        readonly=True
    )
    py_script_group_id = fields.Many2one(
        'py.script.group',
        string="Python Script Group"
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None,
                access_rights_uid=None):
        # Check if our custom context key is present
        if self.env.context.get('apply_script_filter'):
            # Call your function to get the ID list
            allowed_ids = self._get_allowed_ids()
            # Append the ID filter to the existing domain
            domain += [('id', 'in', allowed_ids)]
        return super()._search(domain, offset=offset,
                                   limit=limit, order=order,
                                   access_rights_uid=access_rights_uid)

    def _get_allowed_ids(self):
        self.env.cr.execute("""
            SELECT ps.id
            FROM py_script ps
            LEFT OUTER JOIN py_script_group psg
                ON ps.py_script_group_id = psg.id
            LEFT OUTER JOIN res_groups_users_rel gur
                ON psg.id = gur.gid
            WHERE ps.create_uid = %s or gur.uid = %s
        """, (self.env.user.id, self.env.user.id))
        return [row[0] for row in self.env.cr.fetchall()]

    @ormcache('self.py_script_group_id')
    def _check_user_acl_rights(self):
        """Check user ACL rights for the py_script_group_id."""
        self.ensure_one()
        if not self.py_script_group_id:
            return False
        user = self.env.user
        if len(set(user.groups_id.ids)
               & set(self.py_script_group_id.group_ids.ids)):
            return True
        if user.id == self.user_id.id:
            return True
        if user.has_group('group_restricted_py_script_manager'):
            return True
        return False

    @ormcache('self.py_script_group_id')
    def _get_allowed_modules(self):
        self.ensure_one()
        return self.py_script_group_id \
            .allowed_modules.replace("\n", "").split(" ")

    def run(self, recordset=None, **params):
        """Run restricted python script."""
        if self.code and self._check_user_acl_rights():
            context = {}
            if self.default_context:
                try:
                    context.update(json.loads(self.default_context))
                finally:
                    pass
            if params:
                context.update(params)
            # _logger.info(f"\n++++\n{allowed_models=}\n++++")
            return safe_eval(
                    self.code, recordset, self.env,
                    self._get_allowed_modules(),
                    self.py_script_group_id.with_user_id.id or SUPERUSER_ID,
                    **context)
        else:
            return None

    def run_script(self, recordset=None, **params):
        """Run the current script and display the results."""
        self.ensure_one()
        result = self.run(recordset, **params)
        test = self.env.context.get("test")
        if test and result:
            printed, context, warning_list = result
            message = '<h2>Script executed successfully.</h2>\n'
            message += '<pre class="o_form_sheet_bg">'
            if warning_list:
                message += '<h3>Warning:</h3>\n'
                message += '<pre class="o_form_sheet_bg">' \
                    + "".join(warning_list) + "</pre>\n"
            if printed:
                message += '<h3>Printed:</h3>\n'
                message += '<pre class="o_form_sheet_bg">' \
                    + "".join(printed).replace("<", "&lt;") \
                    .replace(">", "&gt;") + "\n</pre>"
            if context:
                message += '<h3>Context:</h3>\n'
                message += '<pre class="o_form_sheet_bg">' \
                    + str(context) + "</pre>\n"

            # Create or update the result record
            if self.result_id:
                self.result_id.message = message
            else:
                self.result_id = self.env['py.script.result'].create({
                    'message': message
                })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Script Results',
                'res_model': 'py.script.result',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.result_id.id,
                'context': {
                    'default_message': message,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Script Results',
                    'message': 'No code to execute.',
                    'sticky': False,
                }
            }


class PyScriptMixin(models.AbstractModel):
    _name = "py.script.mixin"
    _description = "Restricted Python Scripts Mixin"
    _register = False

    py_script_id = fields.Many2one('py.script', string="Python Script")

    def get_cache(self):
        return self._cache

    def write(self, vals):
        self._on_change(**vals)
        return super().write(vals)

    def _on_change(self, **vals):
        if self.py_script_id:
            self.py_script_id.run(self, **vals)
