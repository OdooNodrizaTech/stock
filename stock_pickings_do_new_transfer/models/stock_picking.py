# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def cron_stock_pickings_do_new_transfer(self):
        picking_type_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'stock_pickings_do_new_transfer_picking_type_id')
        )
        picking_ids = self.env['stock.picking'].search(
            [
                ('picking_type_id', '=', picking_type_id),
                ('state', 'in', ('confirmed', 'partial_available', 'assigned'))
            ]
        )
        if picking_ids:
            for picking_id in picking_ids:
                picking_id.do_transfer()
