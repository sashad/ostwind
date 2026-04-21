# controllers/main.py
from odoo import http
# from odoo.http import request
import os
# import logging

# _logger = logging.getLogger(__name__)


class LucideIconController(http.Controller):
    @http.route('/lucide_icons/list_lucide_icons', type='json', auth='user')
    def list_lucide_icons(self):
        icons_dir = os.path.join(os.path.dirname(__file__),
                                 '../static/src/lucide-static/icons')
        icons = [
            f.replace('.svg', '')
            for f in os.listdir(icons_dir)
            if f.endswith('.svg')
        ]
        # _logger.info(f"\n ---- icons ----:\n {icons}")
        return icons
