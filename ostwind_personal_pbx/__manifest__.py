{
    "name": "Personal PBX",
    "version": "18.0.0.1.0",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Aleksandr Demidov <alex.m.demidoff@gmail.com>",
    "website": "https://ostwind.biz/",
    "depends": [
        "base",
        "mail",
        "ostwind_partner_select_field",
    ],
    "development_status": "Development/Unstable",
    'images': [
        'static/description/banner.png'
    ],
    "assets": {
        # # Define your custom bundle
        # 'ostwind_personal_pbx.assets_standalone_app': [
        #     # Core Odoo assets (replaces 'web._assets_helpers' and 'web._assets_core')
        #     'web/static/src/scss/pre_variables.scss',
        #     'web/static/lib/bootstrap/scss/_variables.scss',
        #     # Include Bootstrap and core assets (Odoo 18 handles this automatically)
        #     # Your custom files
        #     'ostwind_personal_pbx/static/src/standalone_app/**/*',
        # ],
        'ostwind_personal_pbx.assets_standalone_app': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',  # Defines $theme-colors-rgb
            'web/static/lib/bootstrap/scss/_mixins.scss',
            'web/static/lib/bootstrap/scss/_utilities.scss',  # Uses $theme-colors-rgb
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
