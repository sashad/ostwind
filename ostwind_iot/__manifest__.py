{
    "name": "IoT MQTT Managment System",
    "version": "18.0.0.0.1",
    "category": "IoT",
    "license": "AGPL-3",
    "author": "Aleksandr Demidov <alex.m.demidoff@gmail.com>",
    "website": "https://ostwind.biz/",
    "depends": [
        "base",
        "mail",
        "web",
        "iot_oca",
        "lucide_icons",
    ],
    "development_status": "Development/Unstable",
    "data": [
        "security/py_script_security.xml",
        'security/ir.model.access.csv',
        "data/system_data.xml",
        "views/iot_device_views.xml",
        "views/iot_device_mqtt_views.xml",
        "views/iot_device_mqtt_value_views.xml",
        "views/iot_device_mqtt_log_views.xml",
        "views/iot_py_script_views.xml",
        "views/iot_menu.xml",
        "views/iot_mqtt_host.xml",
        # py_scripts
        "views/py_script_views.xml",
        "views/py_script_result_views.xml",
    ],
    "assets": {
        'web.assets_backend': [
            "ostwind_iot/static/src/js/patch_kanban.js",
            "ostwind_iot/static/src/scss/py_script.scss",
        ],
    },
    "installable": True,
    'application': True,
}
