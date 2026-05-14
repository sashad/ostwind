from odoo import fields, models


class IoTCommunicationSystem(models.Model):
    _inherit = "iot.communication.system"

    mqtt_ids = fields.One2many(
        "iot.device", inverse_name="communication_system_id"
    )
    applies_to = fields.Selection([
        ("device", "Device"),
        ("output", "Output"),
        ("mqtt", "MQTT"),
    ], default="device", required=True)
