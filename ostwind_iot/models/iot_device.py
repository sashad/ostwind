import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class IoTDevice(models.Model):
    _inherit = "iot.device"
    _description = "IoT device MQTT"

    mqtt_ids = fields.One2many("iot.device.mqtt", "device_id")

    mqtt_count = fields.Integer(compute="_compute_mqtt_count")
    communication_system_id = fields.Many2one(required=False)

    value_ids_json = fields.Json(compute="_compute_value_ids")

    @api.depends('mqtt_ids')
    def _compute_value_ids(self):
        for record in self:
            values = []
            for mqtt in record.mqtt_ids:
                for v in mqtt.value_ids:
                    if not v.show_in_kanban:
                        continue
                    value = {
                        k: (v.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            if isinstance(v, datetime) else v)
                        for k, v in v.read()[0].items()
                    }
                    value["color"] = v.color()
                    if v.value_type == 'boolean':
                        value["value"] = v.get_value_as_boolean()
                    elif v.value_type == 'numeric':
                        value["value"] = v.get_value_as_float()
                    elif v.value_type == 'int':
                        value["value"] = v.get_value_as_int()
                    else:
                        value["value"] = v.last_payload
                    values.append(value)

            record.value_ids_json = values

    def action_on_click(self):
        context_value = self.env.context['value']
        value = self.env['iot.device.mqtt.value'].browse(context_value['id'])
        host = value.iot_device_mqtt_id.mqtt_host_id
        if context_value['value_type'] == 'boolean':
            # invert boolean value
            value_to_set = context_value['boolean_false'] \
                if context_value['value'] else context_value['boolean_true']
            payload = value_to_set
            if value.setting_template:
                payload = value.setting_template.format(value_to_set)
            host.publish(host.id, value.setting_topic, payload)
        elif context_value['value_type'] in ['numeric', 'int', 'string']:
            return {
                'name': 'Set Value',
                'type': 'ir.actions.act_window',
                'res_model': 'iot.device.mqtt.value',
                'view_mode': 'form',
                'target': 'new',
                'res_id': value.id,
                'view_id': self.env.ref(
                    'ostwind_iot.iot_device_mqtt_set_value_form').id,
                'context': {
                    'default_setting_value': value.last_payload,
                }
            }
        else:
            pass
        _logger.info(f"\n----\n{self.env.context=}\n----")
        return True

    @api.depends("mqtt_ids")
    def _compute_mqtt_count(self):
        for record in self:
            record.mqtt_count = len(record.mqtt_ids)

    # value_ids = fields.One2many("iot.device.mqtt.value",
    #                             inverse_name="iot_device_id")

    def action_show_mqtt(self):
        self.ensure_one()
        action = self.env.ref("ostwind_iot.iot_device_mqtt_topic")
        result = action.read()[0]

        result["context"] = {
            "default_device_id": self.id,
        }
        result["domain"] = "[('device_id', '=', " + str(self.id) + ")]"
        if len(self.mqtt_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.mqtt_ids.id
        return result

    def action_show_chart(self):
        """Action method to show the chart view."""
        context_value = self.env.context['value']
        chart = {
            'name': 'MQTT Log Chart',
            'type': 'ir.actions.act_window',
            'res_model': 'iot.device.mqtt.log',
            'view_mode': 'graph',
            'view_id': self.env.ref(
                'ostwind_iot.iot_device_mqtt_log_graph_string').id,
            'domain': [('iot_device_mqtt_value_id', '=', context_value['id'])],
            'target': 'current',
        }
        if context_value['value_type'] in ['numeric', 'int']:
            chart['view_id'] = self.env.ref(
                    'ostwind_iot.iot_device_mqtt_log_graph_number').id
        return chart
