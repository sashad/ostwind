# @author: Aleksandr Demidov (demidoff@1vp.ru)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Web Theme Classic Patch from Ostwind",
    "summary": "Contrasted style on fields to improve the UI (patch).",
    "version": "17.0.1.0.0",
    "author": "Odoo Community Association (OCA), Ostwind Software",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/sashad/web-theme-patch",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "web",
        "web_theme_classic"
    ],
    "assets": {
        "web.assets_backend": [
            "/web_theme_classic_patch/static/src/scss/web_theme_patch.scss",
        ],
    },
    "installable": True,
    "application": True,
}
