# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

from openerp import api, models, fields
from openerp.exceptions import Warning

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        # action_confirm
        return_data = super(PurchaseOrder, self).button_confirm()
        # operations
        for item in self:
            if item.state == 'purchase':
                for picking_id in item.picking_ids:
                    picking_id.purchase_id = item.id
        # return
        return return_data