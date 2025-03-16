import logging

from odoo.exceptions import ValidationError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

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

    units = fields.One2many(
        "ostwind.rent.object.unit",
        inverse_name='rent_object_id',
        string="Units"
    )


class RentObjectUnit(models.Model):
    _name = "ostwind.rent.object.unit"
    _description = "Units/flats of an rent object."

    rent_object_id = fields.Many2one('ostwind.rent.object', 'Property', readonly=False)
    name = fields.Char('Unit Name', required=True, translate=True)
    value = fields.Float('value', required=False)

    tenant = fields.Many2one('res.partner', 'Tenant', readonly=False)
    owners = fields.One2many(
        "ostwind.rent.object.unit.owner",
        inverse_name='rent_object_unit_id',
        string="Owners"
    )


class RentObjectUnitOwners(models.Model):
    _name = "ostwind.rent.object.unit.owner"
    _description = "Owners of Units/flats of a rent object."

    _part_sum = 0

    rent_object_unit_id = fields.Many2one(
        'ostwind.rent.object.unit',
        'Unit',
        readonly=False
    )
    description = fields.Char('Description', required=True)
    owner = fields.Many2one('res.partner', 'Owner', readonly=False)
    part = fields.Float('Part', required=False, readonly=False)

    # @api.model
    # @api.depends('rent_object_unit_id')
    @api.onchange('part', 'rent_object_unit_id')
    def change_value(self):
        _logger.info(f"--- onchange : {self.rent_object_unit_id._origin.id=} {self.part=} {self._part_sum=} {self.env.context=}")
        _logger.info(f"--- env : {dir(self.env)}")
        if not self.rent_object_unit_id._origin.id :
            return

        RentObjectUnitOwners._part_sum += self.part
        owners = self.env[self._name].search([
            ('rent_object_unit_id', '=', self.rent_object_unit_id._origin.id)
        ])
        rest = 100.0
        for owner in owners:
            # _logger.info(f"{rest=} {self._origin.id=} {owner.id=}")
            if owner.id == self._origin.id:
                continue
            rest -= owner.part
            _logger.info(f"--- owner : {owner=}")
            _logger.info(f"--- rest : {rest=}")
        if self.part > rest or rest <= 0:
            self.part = 0
            raise ValidationError("Sum all parts must be not more 100!")
            return {
                'warning': {
                    'title': 'Error!',
                    'message': 'Sum all parts must be not more 100!'
                }
            }
        if self.env.context.get('add_owner'):
            self.part = rest

        return {
            'type': 'ir.actions.client',
            'tag': 'soft_reload'
        }



    @api.ondelete(at_uninstall=False)
    def delete_owner(self):
        _logger.info(f"------- delete : {self.env.context=}")


    @api.model
    @api.depends('rent_object_unit_id')
    def default_get(self, fields):
        res = super().default_get(fields)
        #        _logger.info(f"------- unit_id : {fields=} {self.env.context=} {self.rent_object_unit_id.id=}")
        _logger.info(f"------- unit_id : {res=} {self._name=}")
        return {
            'part': -10
        }

