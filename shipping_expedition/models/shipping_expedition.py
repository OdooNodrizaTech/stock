# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _name = 'shipping.expedition'
    _description = 'Shipping Expedicion'
    _inherit = ['mail.thread']
    
    name = fields.Char(        
        compute='_get_name',
        string='Nombre',
        store=False
    )
    
    @api.one        
    def _get_name(self):            
        for obj in self:
            obj.name = obj.delivery_code
    
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Albaran'
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',        
        string='Pedido',
    )    
    user_id = fields.Many2one(
        comodel_name='res.users',        
        string='Comercial',
    )    
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',        
        string='Transportista',
    )        
    carrier_type = fields.Char(
        string='Tipo de transportista',
        compute='_get_carrier_type',
        readonly=True,
        store=False
    )    
    
    @api.multi        
    def _get_carrier_type(self):         
        for obj in self:           
            obj.carrier_type = obj.carrier_id.carrier_type
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto'
    )    
    code = fields.Char(
        string='Codigo expedicion'
    )
    delivery_code = fields.Char(
        string='Codigo albaran'
    )             
    date = fields.Date(
        string='Fecha'
    )    
    hour = fields.Char(
        string='Hora'
    )
    observations = fields.Text(
        string='Observaciones'
    )
    state = fields.Selection(
        selection=[
            ('error','Error'), 
            ('generate','Generado'), 
            ('shipped','Enviado'), 
            ('in_delegation','En delegacion'), 
            ('incidence','Incidencia'), 
            ('in_transit','En reparto'), 
            ('delivered','Entregado'),
            ('canceled','Anulada'),
        ],
        string='Estado'
    )
    state_code = fields.Char(
        string='Codigo estado'
    )
    origin = fields.Char(
        string='Origen'
    )
    delivery_note = fields.Char(
        string='Nota de entrega'
    )
    exps_rels = fields.Char(
        string='Expediciones relacionadas'
    )
    delegation_name = fields.Char(
        string='Nombre delegacion'
    )
    delegation_phone = fields.Char(
        string='Telefono delegacion'
    )        
    
    @api.model
    def create(self, values):
        record = super(ShippingExpedition, self).create(values)                    
        #add partner_id follower
        if record.partner_id.id>0:
            reg = {
                'res_id': record.id,
                'res_model': 'shipping.expedition',
                'partner_id': record.partner_id.id,
                'subtype_ids': [(6, 0, [1])],
            }
            self.env['mail.followers'].create(reg)
        #add user_id follower
        if record.user_id.id>0:
            mail_followers_ids_check = self.env['mail.followers'].search(
                [
                    ('res_model', '=', 'shipping.expedition'),
                    ('res_id', '=', record.id),
                    ('partner_id', '=', record.user_id.partner_id.id)
                ]
            )
            if mail_followers_ids_check==False:
                reg = {
                    'res_id': record.id,
                    'res_model': 'shipping.expedition',
                    'partner_id': record.user_id.partner_id.id,
                    'subtype_ids': [(6, 0, [1])],                                              
                }
                self.env['mail.followers'].create(reg)
        #check remove create uid
        if record.user_id.id>0:
            if record.user_id.id!=record.create_uid.id:
                mail_followers_ids = self.env['mail.followers'].search(
                    [
                        ('res_model', '=', 'shipping.expedition'),
                        ('res_id', '=', record.id)
                    ]
                )
                if mail_followers_ids!=False:
                    for mail_follower_id in mail_followers_ids:
                        if mail_follower_id.partner_id.id==record.create_uid.partner_id.id:
                            self.env.cr.execute("DELETE FROM  mail_followers WHERE id = "+str(mail_follower_id.id))
                            #mail_follower_id.unlink()                                
        #record                                                                
        return record
                  
    @api.one
    def update_state(self):
        return True
    
    @api.one
    def action_update_state(self):
        if self.state!="delivered":
            self.update_state()
                                 
        return True
    
    @api.one
    def cancel_state(self):
        return True    
    
    @api.one
    def action_cancell(self):
        if self.state!="canceled":
            self.cancel_state()
    
        return True
    
    @api.one    
    def action_error_update_state_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_incidence_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_error_cancell_expedition_message_slack(self, res):
        return                                    