import asyncio
import json
import logging
import ssl
import threading

import aiomqtt

from odoo import SUPERUSER_ID, api, fields, models, registry
from odoo.tools import config
from odoo.addons.bus.models.bus import dispatch

from .parser import get_value_by_template

_db_name = config.get('db_name')
_registry = registry(_db_name)

_logger = logging.getLogger(__name__)


class IotMqttHost(models.Model):
    _name = "iot.mqtt.host"
    _description = "MQTT Server Host"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _mqtt_task = {}
    _loop = {}
    _thread = {}
    _mqtt_client = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @api.model
    def write(self, vals):
        result = super().write(vals)
        self.stop_mqtt_client(self)
        self.start_mqtt_client(self, self._create_mqtt_config(self))
        return result

    @api.model
    def _register_hook(self):
        for host in self.search([], order='id'):
            _logger.info(f"\n==== {host} ====")
            self.start_mqtt_client(host, self._create_mqtt_config(host))

    name = fields.Char(required=True)
    host = fields.Char()
    port = fields.Integer(compute='_compute_port', store=True, readonly=False)
    protocol = fields.Selection([
        ("mqtt", "MQTT"),
        ("mqtts", "MQTT over SSL"),
        ("ws", "WebSocket"),
        ("wss", "WebSocket over SSL")
    ], default="mqtt", required=True)
    login = fields.Char()
    password = fields.Char(password=True)

    active = fields.Boolean(default=True)

    @api.depends('protocol')
    def _compute_port(self):
        for record in self:
            if record.protocol == 'mqtt':
                record.port = 1883
            elif record.protocol == 'mqtts':
                record.port = 8883
            elif record.protocol == 'ws':
                record.port = 80
            elif record.protocol == 'wss':
                record.port = 443

    def _create_mqtt_config(self, host):
        mqtt_config = {
            "hostname": host.host,
            "port": host.port,
            "username": host.login,
            "password": host.password,
        }
        if host.protocol == 'mqtts' or host.protocol == 'wss':
            mqtt_config["tls_context"] = ssl.create_default_context()
        return mqtt_config

    @classmethod
    def start_mqtt_client(cls, host, mqtt_config):
        """Start the async MQTT client."""
        if host.id not in cls._loop:
            # These vars must be init if mqtt client connected
            cls._loop[host.id] = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop[host.id])
            cls._mqtt_task[host.id] = \
                cls._loop[host.id].create_task(
                        cls._run_mqtt_client(host, mqtt_config))
            cls._thread[host.id] = \
                threading.Thread(target=cls._loop[host.id].run_forever,
                                 daemon=True).start()

    @classmethod
    async def _run_mqtt_client(cls, host, mqtt_config):
        """Async function to connect
        to the MQTT broker and subscribe to topics."""
        _logger.info(f"MQTT config: {mqtt_config}")
        try:
            async with aiomqtt.Client(**mqtt_config) as client:
                cls._mqtt_client[host.id] = client
                await client.subscribe("/#")
                async for message in client.messages:
                    cls._process_mqtt_message(host, message.topic,
                                              message.payload.decode())
        except Exception as e:
            _logger.info(f"MQTT error: {e}. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)
            cls._loop[host.id].create_task(
                    cls._run_mqtt_client(host, mqtt_config))

    @classmethod
    def _process_mqtt_message(cls, host, topic, payload):
        """Process the MQTT message and store it in Odoo."""
        with _registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            topic_id = env["iot.device.mqtt"].search([
                ('mqtt_host_id', '=', host.id),
                ('topic', '=', topic)])
            if topic_id and topic_id.value_ids:
                _logger.info(f"\n{topic_id.value_ids=}")
                for value_id in topic_id.value_ids:
                    extracted_payload = payload
                    if value_id.json_payload:
                        topic_id.write({"json_payload": json.loads(payload)})
                        extracted_payload = get_value_by_template(
                                payload,
                                value_id.json_value_template)
                        if type(extracted_payload) is bool:
                            extracted_payload = 'true' \
                                if extracted_payload else 'false'
                    else:
                        pass

                    if value_id.last_payload != extracted_payload:
                        value_id.write({"last_payload": extracted_payload})
                        data = {"iot_device_mqtt_id": topic_id.id,
                                "iot_device_mqtt_value_id": value_id.id,
                                }
                        if type(extracted_payload) in [float, int]:
                            data['payload_float'] = extracted_payload
                        else:
                            data['payload'] = extracted_payload
                        if value_id.is_logging:
                            env["iot.device.mqtt.log"].create(data)
                    cls._trigger_kanban_item_refresh(env,
                                                     topic_id.device_id.id)
                _logger.info(f"\n>>>>\n{topic=}\n{payload=}\n"
                             f"{extracted_payload=}\n<<<<<<")
            del env

    @classmethod
    def stop_mqtt_client(cls, host):
        """Stop the MQTT client."""
        if host.id in cls._mqtt_task:
            cls._mqtt_task[host.id].cancel()
            del cls._mqtt_task[host.id]
        if host.id in cls._loop:
            cls._loop[host.id].call_soon_threadsafe(cls._loop[host.id].stop)
            if host.id in cls._thread and cls._thread[host.id]:
                cls._thread[host.id].join(timeout=2)
            del cls._loop[host.id]
            del cls._thread[host.id]
            if host.id in cls._mqtt_client:
                del cls._mqtt_client[host.id]

    @classmethod
    def _trigger_kanban_item_refresh(cls, env, res_id):
        """Fire a bus event to the Iot Device Kanban."""
        bus = env['bus.bus']
        channel = (env.cr.dbname, 'iot_mqtt_values_refresh')
        # Format: (db, channel)

        # Check if any WebSocket is subscribed to this channel
        if dispatch._channels_to_ws.get(channel):
            bus._sendone(
                    'iot_mqtt_values_refresh',
                    'refresh_item',
                    {
                        'res_id': res_id,  # res_id of "iot.device"
                    })

    @classmethod
    def publish(cls, host_id, topic, payload):
        """Synchronous method to publish a message to the MQTT broker."""
        cls._loop[host_id].call_soon_threadsafe(
            asyncio.create_task, cls.async_publish(host_id, topic, payload))

    @classmethod
    async def async_publish(cls, host_id, topic, payload):
        """Asynchronous method to publish a message to the MQTT broker."""
        client = cls._mqtt_client[host_id]
        await client.publish(topic, payload)
