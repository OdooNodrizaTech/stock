# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_expedition_note = fields.Text(
        string='Expedition Note',
    )

    shipping_expedition_count = fields.Integer(
        compute='_compute_shipping_expedition_count',
        string="Expeditions",
    )

    @api.multi
    def _compute_shipping_expedition_count(self):
        for item in self:
            item.shipping_expedition_count = len(
                self.env['shipping.expedition'].search(
                    [
                        ('order_id', '=', item.id)
                    ]
                )
            )
