from odoo import fields, models


class PyScriptGroup(models.Model):
    _name = "py.script.group"
    _description = "Restricted Python Script Group"

    name = fields.Char(string="Group Name", required=True)
    group_ids = fields.Many2many(
            'res.groups', string="User Groups", widget="many2many_tags")
    allowed_modules = fields.Text(string="Allowed Python Modules")
    with_user_id = fields.Many2one(
        'res.users',
        string='Run with A User',
        default=lambda self: self.env.user
    )

    def write(self, vals):
        """Clear the ORM cache when a record is updated."""
        result = super().write(vals)
        self.env['py.script'].clear_caches()
        return result
