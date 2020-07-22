# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime

class ShippingExpedition(models.Model):
    _name = 'shipping.expedition'
    _description = 'Shipping Expedicion'
    _inherit = ['mail.thread']
    _rec_name = 'delivery_code'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        required=True
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order',
        related='picking_id.sale_id',
        store=False,
        readonly=True
    )
    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead',
        related='picking_id.sale_id.opportunity_id',
        store=False,
        readonly=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',        
        string='User',
        related='picking_id.sale_id.user_id',
        store=False,
        readonly=True
    )    
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',        
        string='Carrier',
        related='picking_id.carrier_id',
        store=False,
        readonly=True
    )        
    carrier_type = fields.Selection(
        string='Carrier type',
        related='picking_id.carrier_id.carrier_type',
        store=False,
        readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        related='picking_id.partner_id',
        store=False,
        readonly=True
    )    
    code = fields.Char(
        string='Code'
    )
    delivery_code = fields.Char(
        string='Delivery code'
    )             
    date = fields.Date(
        string='Date'
    )    
    hour = fields.Char(
        string='Hour'
    )
    observations = fields.Text(
        string='Observations'
    )
    state = fields.Selection(
        selection=[
            ('error','Error'), 
            ('generate','Generate'),
            ('shipped','Shipped'),
            ('in_delegation','In delegation'),
            ('incidence','Incidence'),
            ('in_transit','In transit'),
            ('delivered','Delivered'),
            ('canceled','Canceled'),
        ],
        string='State'
    )
    state_code = fields.Char(
        string='State code'
    )
    origin = fields.Char(
        string='Origin'
    )
    delivery_note = fields.Char(
        string='Delivery note'
    )
    exps_rels = fields.Char(
        string='Exps_rels'
    )
    delegation_name = fields.Char(
        string='Delegation name'
    )
    delegation_phone = fields.Char(
        string='Delegation phone'
    )
    url_info = fields.Char(
        string='Url info'
    )
    ir_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Attachment'
    )            
    
    @api.model
    def create(self, values):
        record = super(ShippingExpedition, self).create(values)
        # add partner_id follower
        if record.partner_id:
            reg = {
                'res_id': record.id,
                'res_model': 'shipping.expedition',
                'partner_id': record.partner_id.id,
                'subtype_ids': [(6, 0, [1])],
            }
            self.env['mail.followers'].create(reg)
        # add user_id follower
        if record.user_id:
            mail_followers_ids_check = self.env['mail.followers'].search(
                [
                    ('res_model', '=', 'shipping.expedition'),
                    ('res_id', '=', record.id),
                    ('partner_id', '=', record.user_id.partner_id.id)
                ]
            )
            if mail_followers_ids_check == False:
                reg = {
                    'res_id': record.id,
                    'res_model': 'shipping.expedition',
                    'partner_id': record.user_id.partner_id.id,
                    'subtype_ids': [(6, 0, [1])],                                              
                }
                self.env['mail.followers'].create(reg)
        # check remove create uid
        if record.user_id:
            if record.user_id.id != record.create_uid.id:
                mail_followers_ids = self.env['mail.followers'].search(
                    [
                        ('res_model', '=', 'shipping.expedition'),
                        ('res_id', '=', record.id)
                    ]
                )
                if mail_followers_ids:
                    for mail_follower_id in mail_followers_ids:
                        if mail_follower_id.partner_id.id == record.create_uid.partner_id.id:
                            mail_follower_id.sudo().unlink()
        # record
        return record
    
    @api.model    
    def cron_shipping_expeditions_update_state(self):
        current_date = datetime.today()
        
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('state', 'not in', ('delivered', 'canceled')),
                ('carrier_id.carrier_type', 'in', ('cbl', 'txt', 'tsb', 'nacex')),
                ('date', '<', current_date.strftime("%Y-%m-%d"))
            ]
        )
        if shipping_expedition_ids:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_update_state()
                
    @api.one
    def action_update_state(self):
        return False        
    
    @api.one    
    def action_error_update_state_expedition(self, res):
        return                                    