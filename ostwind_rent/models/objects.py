# -*- coding: utf-8 -*-

from odoo import fields, models


class RentObject(models.Model):
    _name = "ostwind.rent.object"
    _description = "Real estate properties"
    _order = "sequence"

    name = fields.Char('Prop Name', required=True, translate=True)
    # number_of_months = fields.Integer('# Months', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)

    # _sql_constraints = [
    #    ('check_number_of_months', 'CHECK(number_of_months >= 0)', 'The number of month can\'t be negative.'),
    # ]
