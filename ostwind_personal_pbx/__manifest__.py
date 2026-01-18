{
    "name": "Personal PBX",
    "version": "17.0.0.0.1",
    "category": "Ostwind software",
    "license": "AGPL-3",
    "author": "Aleksandr Demidov <alex.m.demidoff@gmail.com>",
    "website": "https://ostwind.biz/",
    "depends": [
        "base",
        "ostwind_partner_select_field",
    ],
    "development_status": "Development/Unstable",
    "assets": {
        'ostwind_personal_pbx.assets_standalone_app': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),
            ('include', 'web._assets_core'),
            'ostwind_personal_pbx/static/src/standalone_app/**/*',
        ],
        'web.assets_backend': [
            'ostwind_personal_pbx/static/src/xml/phone_field_ext.xml',
            'ostwind_personal_pbx/static/src/js/patches.js',
        ],
    },
    "data": [
        'views/pbx_views.xml',
        'views/index_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    'application': False,
}
