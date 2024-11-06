{
    "name": "Rental Menegment System",
    "version": "17.0.0.0.1",
    "category": "Managment",
    "license": "AGPL-3",
    "author": "Ostwind Software",
    "website": "https://idc-ostwind-gmbh.odoo.com/",
    "depends": ["base", "account", "product", "portal"],
    "development_status": "Development/Unstable",
    "data": [
#        "data/contract_cron.xml",
#        "views/contract_portal_templates.xml",
    ],
    "assets": {
#        "web.assets_frontend": ["contract/static/src/scss/frontend.scss"],
#        "web.assets_tests": ["contract/static/src/js/contract_portal_tour.esm.js"],
    },
    "installable": True,
    'application': True,
}
