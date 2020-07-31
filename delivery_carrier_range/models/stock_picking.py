# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    estimated_cost = fields.Float(
        string='Estimated cost',
        store=True
    )

    @api.multi
    def action_confirm(self):
        return_action = super(StockPicking, self).action_confirm()
        # operations
        for obj in self:
            if obj.picking_type_id.code == 'outgoing':
                # get_carrier_id_cheaper
                if obj.carrier_id and obj.partner_id:
                    obj.get_carrier_id_cheaper()
                # define_estimated_cost
                obj.define_estimated_cost()
        # return
        return return_action

    @api.onchange('carrier_id')
    def onchange_carrier_id_override(self):
        if self.carrier_id and self.picking_type_id.code == 'outgoing' \
                and self.partner_id:
            if self.partner_id.country_id and self.partner_id.state_id:
                self.define_estimated_cost()

    @api.multi
    def define_estimated_cost(self):
        for item in self:
            if item.carrier_id and item.partner_id:
                if item.partner_id.country_id and item.partner_id.state_id:
                    range_ids = self.env['delivery.carrier.range'].search(
                        [
                            ('country_id', '=', item.partner_id.country_id.id),
                            ('carrier_id', '=', item.carrier_id.id),
                            ('weight_range_start', '>=', item.weight),
                            '|',
                            ('state_id', '=', False),
                            ('state_id', '=', item.partner_id.state_id.id)
                        ]
                    )
                    if range_ids:
                        best_price = 0
                        for range_id in range_ids:
                            if best_price == 0:
                                best_price = range_id.price
                        # update
                        item.estimated_cost = best_price

    @api.multi
    def get_carrier_id_cheaper(self):
        for item in self:
            if item.carrier_id.id == 0 \
                    and item.picking_type_id.code == 'outgoing' \
                    and item.partner_id:
                if item.partner_id.country_id and item.partner_id.state_id:
                    # define
                    best_price = 0
                    # search and change carrier_id
                    if item.partner_id:
                        carrier_id_best_price = 0
                        # with_state_id
                        if item.partner_id.state_id:
                            range_ids = self.env['delivery.carrier.range'].search(
                                [
                                    ('country_id', '=', item.partner_id.country_id.id),
                                    ('weight_range_start', '>=', item.weight),
                                    '|',
                                    ('state_id', '=', False),
                                    ('state_id', '=', item.partner_id.state_id.id)
                                ]
                            )
                            if range_ids:
                                for range_id in range_ids:
                                    if best_price == 0 or range_id.price < best_price:
                                        best_price = range_id.price
                                        carrier_id_best_price = range_id.carrier_id.id
                        else:
                            # get first without state_id
                            range_ids = self.env['delivery.carrier.range'].search(
                                [
                                    ('country_id', '=', item.partner_id.country_id.id),
                                    ('weight_range_end', '>=', item.weight),
                                    ('state_id', '=', False)
                                ]
                            )
                            if range_ids:
                                carrier_id_best_price = range_ids[0].carrier_id.id
                        # carrier_id_best_price
                        if carrier_id_best_price > 0:
                            item.carrier_id = carrier_id_best_price
