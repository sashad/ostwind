# -*- coding: utf-8 -*-

from odoo import fields, models


class RentObject(models.Model):
    _name = "ostwind.rent.object"
    _description = "Real estate properties"
    _order = "sequence"
    # Main
    name = fields.Char('Prop Name', required=True, translate=True)
    addr_street = fields.Char('Street', required=False, translate=True)
    addr_house = fields.Char('House', required=False, translate=False)
    addr_zip = fields.Char('Zip', required=False, translate=False)
    addr_city = fields.Char('City', required=False, translate=True)
    addr_country_id = fields.many2one('res.country', 'Country', readonly=True) # link to vocab country
    # General
    property_type =  fields.Selection(
        string='Type of property',
        selection=[
            ('r', 'Rental property'),
            ('c', 'Comercial property'),
            ('rc', 'Residential complex'),
            ('ca', 'Condominium association'),
            ('m', 'Misc')
        ],
        help=""
    )
    date_build = fields.Date('Build year', required=False)
    plot_number = fields.Char('Plot number', required=False, translate=False)
    cadastral_municipality = fields.Char('Cadastral municipality', required=False, translate=False)
    entry_number = fields.Char('Entry number', required=False, translate=False)
    coownership = fields.Integer('Co-ownership', required=False)
    # Heating value
    hiating_requirement = fields.Float('Heating requirement', required=False)
    hiating_type = fields.Selection(
        string='Heating type',
        selection=[
            ('c', 'Central'),
            ('f', 'Floor type'),
            ('pch', 'Partial central heating'),
            ('gfh', 'Gas floor heating'),
        ],
        help=""
    )
    energy_source = fields.Selection(
        string='Energy source',
        selection=[
            ('gth', 'Geothermal energy'),
            ('dh', 'District heating'),
            ('gas', 'Gas'),
            ('ho', 'Heating oil'),
            ('w', 'Wood'),
            ('p', 'Pellets'),
            ('phv', 'Photo voltaic'),
            ('e', 'Electricity'),
            ('hp', 'Heating pump'),
        ],
        help=""
    )
    energy_certificate = fields.Boolean('Energy certificate')
    energy_certificate_file = fields.Binary(string = 'Energy certificate file')
    billing_company = fields.many2one('res.company', 'Billing company', readonly=True)
    heating_type_comment = fields.Char('Heating type comment', required=False, translate=False)
    living_space = fields.Float('Living space', required=False)
    usefull_value = fields.Float('Usefull value', required=False)
    heatable_space = fields.Float('Heatable space', required=False)
    consumption_cost_share = fields.Integer('Consumption cost share', required=False)
    basic_cost_share = fields.Integer('Basic cost share', required=False)
    # Units/Flats

    # number_of_months = fields.Integer('# Months', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)

    # _sql_constraints = [
    #    ('check_number_of_months', 'CHECK(number_of_months >= 0)', 'The number of month can\'t be negative.'),
    # ]

class RentObjectUnit(models.Model):
    _name = "ostwind.rent.object.unit"
    _description = "Units/flats of an rent object."

    rent_object_id = fields.many2one('ostwind.rent.object') # link to rent object.
    name = fields.Char('Unit Name', required=True, translate=True)
    tenant = fields.many2one('res.partners') # Жилец, арендатор.

class RentObjectUnitOwners(models.Model):
    _name = "ostwind.rent.object.unit.owner"
    _description = "Owners of Units/flats of an rent object."

    rent_object_unit_id = fields.many2one('ostwind.rent.object.unit')
    description = fields.Char('Unit Name', required=True)
    owner_partner_id = fields.many2one('res.partners')
    part = fields.Float('Part', required=False)

