# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    send_sms_info = fields.Boolean(
        string='Send sms info'
    )
    sms_info_sms_template_id = fields.Many2one(
        comodel_name='sms.template',
        string='Sms template'
    )
