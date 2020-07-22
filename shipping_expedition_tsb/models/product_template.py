# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tsb_sender_center = fields.Char(
        string='TSB Center'
    )        