# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrierRange(models.Model):
    _name = 'delivery.carrier.range'
    _description = 'Delivery Carrier Range'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Carrier',
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
    )
    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Country state',
    )
    weight_range_start = fields.Float(
        string='Range start'
    )
    weight_range_end = fields.Float(
        string='Range end'
    )
    price = fields.Float(
        string='Price'
    )
