# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Carrier'
    )
