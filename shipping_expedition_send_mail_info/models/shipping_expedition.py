# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    date_send_mail_info = fields.Datetime(
        string='Date send mail info'
    )

    @api.multi
    def action_send_mail_info_real(self):
        self.ensure_one()
        _logger.info(_('Send email related to shipping_expedition %s') % self.id)
        vals = {
            'author_id': self.user_id.partner_id.id,
            'record_name': self.name
        }
        message_obj = self.env['mail.compose.message'].with_context().sudo().create(
            vals
        )
        res = message_obj.onchange_template_id(
            self.carrier_id.mail_info_mail_template_id.id,
            'comment',
            'shipping.expedition',
            self.id
        )
        message_obj.update({
            'author_id': vals['author_id'],
            'template_id': self.carrier_id.mail_info_mail_template_id.id,
            'composition_mode': 'comment',
            'model': 'shipping.expedition',
            'res_id': self.id,
            'body': res['value']['body'],
            'subject': res['value']['subject'],
            'email_from': res['value']['email_from'],
            'partner_ids': res['value']['partner_ids'],
            # 'attachment_ids': res['value']['attachment_ids'],
            'record_name': vals['record_name'],
            'no_auto_thread': False
        })
        message_obj.send_mail_action()
        self.date_send_mail_info = datetime.today()

    @api.multi
    def action_send_mail_info(self):
        self.ensure_one()
        allow_send = False
        if self.carrier_id.send_mail_info:
            if self.carrier_id.mail_info_mail_template_id:
                if not self.date_send_mail_info:
                    if self.state not in [
                        'error', 'generate', 'canceled', 'delivered', 'incidence'
                    ]:
                        if self.partner_id.email:
                            if self.carrier_id.carrier_type == 'nacex':
                                allow_send = True
                            else:
                                if self.delegation_name and self.delegation_phone:
                                    allow_send = True
                            # allow_send
                            if allow_send:
                                self.action_send_mail_info_real()

    @api.model
    def cron_shipping_expeditionsend_mail_info(self):
        # not nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '!=', 'nacex'),
                ('carrier_id.send_mail_info', '=', True),
                ('carrier_id.mail_info_mail_template_id', '!=', False),
                (
                    'state',
                    'not in',
                    (
                        'error', 'generate',
                        'canceled', 'delivered', 'incidence'
                    )
                ),
                ('user_id', '!=', False),
                ('date_send_mail_info', '=', False),
                ('delegation_name', '!=', False),
                ('delegation_phone', '!=', False),
                ('partner_id.email', '!=', False),
                ('picking_id.date_done', '!=', False)
            ]
        )
        if shipping_expedition_ids:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_send_mail_info()
        # nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'nacex'),
                ('carrier_id.send_mail_info', '=', True),
                ('carrier_id.mail_info_mail_template_id', '!=', False),
                (
                    'state',
                    'not in',
                    (
                        'error', 'generate',
                        'canceled', 'delivered', 'incidence'
                    )
                ),
                ('user_id', '!=', False),
                ('date_send_mail_info', '=', False),
                ('partner_id.email', '!=', False),
                ('picking_id.date_done', '!=', False)
            ]
        )
        if shipping_expedition_ids:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_send_mail_info()
