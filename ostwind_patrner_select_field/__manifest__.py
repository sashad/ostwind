{
    "name": "A PBX extension for the partner select field.",
    "version": "17.0.0.0.1",
    "category": "Ostwind software",
    "license": "AGPL-3",
    "author": "Aleksandr Demidov <alex.m.demidoff@gmail.com>",
    "website": "https://www.ostwind.biz/",
    "depends": [
        "base",
        "website",
    ],
    "development_status": "Development/Unstable",
    "assets": {
        'web.assets_backend': [
            'ostwind_patrner_select_field/static/src/scss/partner_many2one_field.scss',
            'ostwind_patrner_select_field/static/src/mail/mail_template.xml',
            'ostwind_patrner_select_field/static/src/mail/mail.js',
            'ostwind_patrner_select_field/static/src/xml/partner_many2one_field_template.xml',
            'ostwind_patrner_select_field/static/src/js/partner_many2one_field.js',
        ],
    },
    "installable": True,
    'application': False,
}
