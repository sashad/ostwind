from odoo import fields, models


class IoTDeviceMqtt(models.Model):
    _name = "iot.device.mqtt"
    _description = "IoT mqtt topic"

    name = fields.Char(required=True)
    key = fields.Char(required=True, help="An Unique String of a Topic.")
    device_id = fields.Many2one("iot.device", required=True)
    mqtt_host_id = fields.Many2one("iot.mqtt.host", required=True)
    topic = fields.Char(required=True)
    json_payload = fields.Json()

    value_ids = fields.One2many(
        "iot.device.mqtt.value",
        "iot_device_mqtt_id",
        string="Values"
    )

    _sql_constraints = [
        ('unique_index', 'unique(mqtt_host_id, topic)',
         'The combination of mqtt_host_id and topic must be unique.')
    ]

    def copy(self, default=None):
        default = dict(default or {})
        # Modify fields before the record is actually created
        default.update({
            'name': self.name + " (copy)",
            'topic': self.topic + " (copy)",
        })
        return super().copy(default)

    def subscribe(self, topic):
        self.mqtt_host_id.subscribe(topic)

    def publish(self, topic, value, tos=1):
        self.mqtt_host_id.publish(topic, value, tos)
