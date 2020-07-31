# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_negative_stock = fields.Boolean(
        string='Allow negative stock'
    )

    @api.multi
    def get_quantity_by_lot_id(self, lot_id=0):
        self.ensure_one()
        qty = 0
        if lot_id == 0:
            stock_quant_ids = self.env['stock.quant'].sudo().search(
                [
                    ('location_id.usage', '=', 'internal'),
                    ('product_id', '=', self.id)
                ]
            )
        else:
            stock_quant_ids = self.env['stock.quant'].sudo().search(
                [
                    ('location_id.usage', '=', 'internal'),
                    ('product_id', '=', self.id),
                    ('lot_id', '=', lot_id)
                ]
            )
        # operations
        if stock_quant_ids:
            for stock_quant_id in stock_quant_ids:
                qty += stock_quant_id.qty

        return qty
