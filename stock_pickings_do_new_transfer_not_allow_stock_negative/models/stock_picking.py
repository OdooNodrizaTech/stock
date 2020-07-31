# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, _
from odoo.exceptions import Warning as UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        allow_do_transfer = True
        # operations
        for item in self:
            if item.picking_type_id.code == 'outgoing':
                for product_id in item.pack_operation_product_ids:
                    if not product_id.product_id.product_tmpl_id.allow_negative_stock:
                        product_id_tmpl = product_id.product_id.product_tmpl_id
                        # pack_lot_ids
                        if product_id.pack_lot_ids:
                            for pack_lot_id in product_id.pack_lot_ids:
                                if pack_lot_id.qty > 0:
                                    qty_item = product_id_tmpl.get_quantity_by_lot_id(
                                        pack_lot_id.lot_id.id
                                    )[0]
                                    qty_item_final = qty_item-pack_lot_id.qty
                                    if qty_item_final < 0:
                                        raise UserError(
                                            _('Product  %s - %s would keep stock %s')
                                            % (
                                                product_id.product_id.name,
                                                pack_lot_id.lot_id.name,
                                                qty_item_final
                                            ))
                        else:
                            if product_id.qty_done > 0:
                                qty_item = product_id_tmpl.get_quantity_by_lot_id(0)[0]
                                qty_item_final = qty_item-product_id.qty_done
                                if qty_item_final < 0:
                                    raise UserError(
                                        _('Product  %s would keep stock %s') % (
                                            product_id.product_id.name,
                                            qty_item_final
                                        ))
        # allow_do_transfer
        if allow_do_transfer:
            return super(StockPicking, self).do_transfer()
