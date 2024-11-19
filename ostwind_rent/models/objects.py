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
    addr_country_id = fields.Many2one('res.country', 'Country', readonly=False)
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
    cadastral_municipality = fields.Char(
        'Cadastral municipality',
        required=False,
        translate=False
    )
    entry_number = fields.Char('Entry number', required=False, translate=False)
    coownership = fields.Integer('Co-ownership', required=False)
    # Heating value
    heating_requirement = fields.Float('Heating requirement', required=False)
    heating_type = fields.Selection(
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
            ('wd', 'Wood'),
            ('plt', 'Pellets'),
            ('phv', 'Photo voltaic'),
            ('elc', 'Electricity'),
            ('hp', 'Heating pump'),
        ],
        help=""
    )
    energy_certificate = fields.Boolean('Energy certificate')
    energy_certificate_file = fields.Binary(string = 'Energy certificate file')
    billing_company = fields.Many2one('res.company', 'Billing company', readonly=False)
    heating_type_comment = fields.Char(
        'Heating type comment',
        required=False,
        translate=False
    )
    utility_value = fields.Float(
        'Utility value',
        required=False,
        help="Value according to land register"
    )
    net_floor_area = fields.Float('Net Floor Area (NFA)', required=False)
    heated_living_aria = fields.Float(
        'Heated living aria',
        required=False,
        help="Area or space that can be heated"
    )
    variable_cost_share = fields.Integer('Variable cost share', required=False)
    fixed_cost_share = fields.Integer('Fixed cost share', required=False)

    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=1000)

    units = fields.Many2many("ostwind.rent.object.unit", string="Units")


class RentObjectUnit(models.Model):
    _name = "ostwind.rent.object.unit"
    _description = "Units/flats of an rent object."

    rent_object_id = fields.Many2one('ostwind.rent.object', readonly=False)
    name = fields.Char('Unit Name', required=True, translate=True)
    value = fields.Float('value', required=False)

    tenant = fields.Many2one('res.partner', 'Tenant', readonly=False)
    owners = fields.Many2many("ostwind.rent.object.unit.owner", string="Owners")


class RentObjectUnitOwners(models.Model):
    _name = "ostwind.rent.object.unit.owner"
    _description = "Owners of Units/flats of a rent object."

    rent_object_unit_id = fields.Many2one('ostwind.rent.object.unit', 'Unit', readonly=False)
    description = fields.Char('Unit Name', required=True)
    owner_partner_id = fields.Many2one('res.partner', 'Owner', readonly=False)
    part = fields.Float('Part', required=False)

