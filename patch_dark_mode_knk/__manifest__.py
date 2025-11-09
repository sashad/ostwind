# @author: Aleksandr Demidov (demidoff@1vp.ru)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Dark Mode Kanak patch',
    'version': '17.0.1.1',
    'summary': 'Dark Mode is an extension that helps you quickly turn the screen (browser) to dark in Odoo. This dark mode backend theme gives you a fully modified view with a full-screen display. It is a perfect choice for your Odoo Backend and an attractive theme for Odoo. | apps night mode | dark mode| night mode | enable dark mode | odoo night mode |',
    'description': """
       Dark Mode is an extension that helps you quickly turn the screen (browser) to dark in Odoo. This dark mode backend theme gives you a fully modified view with a full-screen display. It is a perfect choice for your Odoo Backend and an attractive theme for Odoo.
    """,
    'author': 'Ostwind Software',
    'license': 'OPL-1',
    'website': 'https://github.com/sashad/ostwind',
    "category": "Extra Tools",
    'depends': ['dark_mode_knk'],
    "assets": {
        "web.assets_backend": [
            '/patch_dark_mode_knk/static/src/js/dark_mode_button.js',
            "/patch_dark_mode_knk/static/src/scss/dark_mode_patch.scss",
            '/patch_dark_mode_knk/static/src/xml/dark_mode_button.xml',
        ],
    },
    "installable": True,
    "application": False,
}
