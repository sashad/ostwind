from . import models
from . import controllers
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config


def post_load_hook():
    """Run after the module is loaded."""
    db_name = config.get('db_name')
    print(f"------------------ {db_name} -------------------")

    registry = odoo.registry(db_name)
    # db = sql_db.db_connect('test')
    with registry.cursor() as cr:
        # 3. Create the environment manually
        env = api.Environment(cr, SUPERUSER_ID, {})
        mqtt_client = env['iot.mqtt.host'].browse(1)
        mqtt_client.start_mqtt_client()

# post_load_hook()
