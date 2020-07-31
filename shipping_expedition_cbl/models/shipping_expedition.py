# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models

import logging

import urllib
import urllib.request as urllib2

import requests
import unidecode
from bs4 import BeautifulSoup
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def action_update_state(self):
        # operations
        for item in self:
            if item.carrier_id.carrier_type == 'cbl':
                item.action_update_state_cbl()
        # return
        return super(ShippingExpedition, self).action_update_state()

    @api.multi
    def action_update_state_cbl(self):
        self.ensure_one()
        url = 'https://clientes.cbl-logistica.com/public/consultaenvios.aspx'
        values = {}
        response = {
            'errors': True,
            'error': "Pendiente de realizar",
            'return': ""
        }
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        inputs = soup.find_all('input')
        for input_field in inputs:
            if input_field['type'] == 'hidden':
                values[input_field['id']] = input_field['value']
            else:
                values[input_field['id']] = ''

        if 'WebCUI_usuario' in values:
            values['WebCUI_usuario'] = self.carrier_id.cbl_sender_customer
            response['errors'] = False
            response['error'] = ''
            response['return'] = {}

        if self.code and self.code != "":
            if 'WebCUI_nenvio' in values:
                values['WebCUI_nenvio'] = self.code
        else:
            if 'WebCUI_ref' in values:
                values['WebCUI_ref'] = self.picking_id.name

        if not response['errors']:
            data = urllib.urlencode(values)
            response_data = urllib2.urlopen(url, data)
            page = response_data.read()
            soup = BeautifulSoup(page, 'html.parser')
            trs = soup.find_all('tr')
            td0_previous = False
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds) == 1:
                    td0 = unidecode.unidecode(tds[0].text.lower())
                    if td0_previous == 'observaciones':
                        response['return'][str(td0_previous)] = str(td0)

                    td0_previous = td0
                elif len(tds) == 2:
                    td0 = unidecode.unidecode(tds[0].text.lower())
                    td0 = td0.replace(".", "").replace(":", "").replace(" ", "_")
                    td0_previous = td0
                    td1 = tds[1].text
                    if td0 == "situacion":
                        td1 = unidecode.unidecode(td1.lower())
                        td1 = td1.replace(" ", "_")
                    response['return'][str(td0)] = str(td1)

        if 'situacion' not in response['return']:
            response['errors'] = True
        # operations
        if response['errors']:
            _logger.info(response)
            self.action_error_update_state_expedition(response)
        else:
            # fecha_entrega
            if 'fecha_entrega' in response['return']:
                if '/' in response['return']['fecha_entrega']:
                    fecha_split = response['return']['fecha_entrega'].split('/')
                    self.date = '%s-%s-%s' % (
                        fecha_split[2][0:4],
                        fecha_split[1],
                        fecha_split[0]
                    )
            # detalle_del_envio
            if 'detalle_del_envio_' in response['return']:
                self.code = response['return']['detalle_del_envio_']
            # ag_destino
            if 'ag_destino' in response['return']:
                self.delegation_name = response['return']['ag_destino']
            # telefono
            if 'telefono' in response['return']:
                self.delegation_phone = response['return']['telefono']
            # observaciones
            if 'observaciones' in response['return']:
                self.observations = response['return']['observaciones']
            # state
            state_old = self.state
            state_new = False

            if response['return']['situacion'] in [
                'entregada', 'entregada_con_incidencia'
            ]:
                state_new = "delivered"
            elif response['return']['situacion'] == "en_gestion":
                state_new = "shipped"
            elif response['return']['situacion'] == "en_destino":
                state_new = "in_delegation"
            elif response['return']['situacion'] in [
                'en_reparto', 'en_transito'
            ]:
                state_new = "in_transit"
            elif response['return']['situacion'] == "devuelta":
                state_new = "canceled"
            elif response['return']['situacion'] == "incidencia":
                state_new = "incidence"
            # update state
            if state_new and state_new != state_old:
                self.state = state_new
