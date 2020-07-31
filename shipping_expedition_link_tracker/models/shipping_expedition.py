# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import fields, models, api
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    link_tracker_id = fields.Many2one(
        comodel_name='link.tracker',
        string='Link Tracker Id'
    )

    @api.model
    def create(self, values):
        res = super(ShippingExpedition, self).create(values)
        # operations
        if res.url_info:
            res.action_generate_shipping_expedition_link_tracker()
        # return
        return res

    @api.multi
    def action_generate_shipping_expedition_link_tracker(self):
        for item in self:
            if item.link_tracker_id.id == 0:
                if item.url_info:
                    vals = {
                        'title': self.code,
                        'url': self.url_info
                    }
                    link_tracker_obj = item.env['link.tracker'].sudo().create(vals)
                    item.link_tracker_id = link_tracker_obj.id
        # return
        return True
