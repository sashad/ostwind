from odoo import fields, models


class IotSeviceMqttLog(models.Model):
    _name = "iot.device.mqtt.log"
    _description = "MQTT Topic value logging"

    payload = fields.Char('Payload', required=False)  # , aggregator="avg"
    payload_float = fields.Float('Payload as Number', aggregator="avg")
    iot_device_mqtt_id = fields.Many2one(
        "iot.device.mqtt", required=True, readonly=True, auto_join=True
    )
    iot_device_mqtt_value_id = fields.Many2one(
        "iot.device.mqtt.value", required=True, readonly=True, auto_join=True
    )

    _sql_constraints = [
        ('unique_index', 'unique(iot_device_mqtt_id, '
         'iot_device_mqtt_value_id, create_date)',
         'The combination of iot_device_mqtt_id,'
         'iot_device_mqtt_value_id, and create_date must be unique.')
    ]
