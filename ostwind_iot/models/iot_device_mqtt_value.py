import logging

from odoo import fields, models
from odoo.tools.float_utils import float_round

from .colors import COLORS
from .iot_mqtt_host import IotMqttHost
from .restricted import RestrictedRecordset

_logger = logging.getLogger(__name__)


def publish(host_id, topic, payload):
    return IotMqttHost.publish(host_id, topic, payload)


class IotDeviceMqttValue(models.Model):
    _name = "iot.device.mqtt.value"
    _description = "MQTT Topic values"
    _order = "iot_device_mqtt_id, order, id"

    name = fields.Char('Value name', required=True)
    key = fields.Char(required=True, help="An Unique String of a Value.")
    # iot_device_id = fields.Many2one(
    #     "iot.device", required=True, readonly=True, auto_join=True
    # )
    iot_device_mqtt_id = fields.Many2one("iot.device.mqtt", required=True)

    json_payload = fields.Boolean('JSON payload', default=False)
    json_value_template = fields.Char(required=False)
    value_type = fields.Selection(
        [
            ("numeric", "Numeric"),
            ("int", "Integer"),
            ("boolean", "Boolean"),
            ("string", "String"),
        ],
        required=True,
        default="numeric",
    )

    numeric_decimal_places = fields.Integer('Number of decimal places',
                                            default=0)

    boolean_true = fields.Char('Bolean True value', default='true')
    boolean_false = fields.Char('Bolean False value', default='false')

    show_in_kanban = fields.Boolean('Show in kanban', default=True)
    order = fields.Integer('Secuance', default=100)

    last_payload = fields.Char()
    is_logging = fields.Boolean('Logging a Value', default=False)

    value_low = fields.Float('Low')
    value_midle = fields.Float('Midle')
    color_low = fields.Integer('Low', default=4)
    color_midle = fields.Integer('Midle', default=10)
    color_high = fields.Integer('High', default=1)

    color_true = fields.Integer('Color of True value', default=4)

    color_default = fields.Integer(default=0)

    icon = fields.Char(widget="lucide_icon")
    icon_true = fields.Char(widget="lucide_icon", default="toggle-right")
    icon_false = fields.Char(widget="lucide_icon", default="toggle-left")

    setting_help = fields.Char(
        string="Setting Value Name",
        help="To define a setting value name."
        " A Target Temperature, for example."
    )
    setting_topic = fields.Char()
    # template = "Hello, {}! Your order {} is ready."
    # template.format(name, order_id)
    setting_template = fields.Char()
    setting_value = fields.Char()  # get it from a form.

    def _get_allowed_script_ids(self):
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

    hook_py_script = fields.Many2one(
            'py.script', string='Hook Py Script',
            domain=lambda self: [('id', 'in', self._get_allowed_script_ids())])

    active = fields.Boolean(default=True)

    def color(self):
        if self.value_type == 'string':
            return COLORS[self.color_default]
            # return 'inherit'
        elif self.value_type == 'boolean':
            return COLORS[self.color_true] \
                if self.get_value_as_boolean() \
                else COLORS[self.color_default]
        number = self.get_value_as_float()
        if number and self.value_low and number <= self.value_low:
            return COLORS[self.color_low]
        elif number and self.value_midle and number <= self.value_midle:
            return COLORS[self.color_midle]
        if number and self.value_midle:
            return COLORS[self.color_high]
        return 'inherit'

    def get_value_as_int(self):
        try:
            return int(self.last_payload)
        except Exception:
            return None

    def get_value_as_float(self):
        try:
            return float_round(float(
                self.last_payload.replace(' ', '').replace(',', '.')),
                               self.numeric_decimal_places)
        except Exception:
            return None

    def get_value_as_boolean(self):
        if (self.last_payload == self.boolean_true):
            return True
        if (self.last_payload == self.boolean_false):
            return False

        return None

    def get_value_as_string(self):
        return self.last_payload

    def write(self, vals):
        global publish
        if 'setting_value' in vals:
            if self.setting_topic:
                payload = vals['setting_value']
                if self.setting_template:
                    payload = self.setting_template.format(payload)
                host_id = self.iot_device_mqtt_id.mqtt_host_id.id
                publish(host_id, self.setting_topic, payload)
            if self.hook_py_script:
                self._on_last_payload_change(**vals)
        elif 'last_payload' in vals:
            self._on_last_payload_change(**vals)
        return super().write(vals)

    def _on_last_payload_change(self, **vals):
        global publish
        if self.hook_py_script:
            vals['mqtt_topic'] = RestrictedRecordset(
                    self.iot_device_mqtt_id)
            vals['mqtt_host'] = RestrictedRecordset(
                    self.iot_device_mqtt_id.mqtt_host_id)
            vals['publish'] = publish
            result = self.hook_py_script.run(self, **vals)
            _logger.info(f'\n--- RUN ---\n{vals=}\n{result}\n---------')

    def get_cache(self):
        if not hasattr(self.env.registry, '_iot_global_cache'):
            self.env.registry._iot_global_cache = {}
        return self.env.registry._iot_global_cache
