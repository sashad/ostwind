from odoo import fields, models


class PyScriptResult(models.Model):
    _name = "py.script.result"
    _description = "Python Script Result"

    message = fields.Html(string="Result", readonly=True)

    def action_discard(self):
        """Discard the result and close the form."""
        return {'type': 'ir.actions.act_window_close'}
