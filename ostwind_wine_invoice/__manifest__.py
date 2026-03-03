# -*- coding: utf-8 -*-
{
    'name': 'Wine Invoice',
    'version': '0.1',
    'category': 'Ostwind software',
    'website': 'https://ostwind.biz/',
    "license": "GPL-3",
    "author": "Aleksandr Demidov <alex.m.demidoff@gmail.com>",
    'summary': 'Add some fields in an invoice.',
    'description': """
        Specific Invoice Modifications for Wine Distributors.
    """,
    'depends': [
        'base',
        'mail',
        'account',
        'sale',
    ],
    'data': [
        'views/report_invoice_document.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'assets': {
        'web.assets_backend': [
            ],
    },
    'installable': True,
    'application': False,
}
