# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, tools

import pycurl
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def action_update_state(self):
        # operations
        for item in self:
            if item.carrier_id.carrier_type == 'nacex':
                item.action_update_state_nacex()
        # return
        return super(ShippingExpedition, self).action_update_state()

    @api.multi
    def action_update_state_nacex(self):
        self.ensure_one()
        if self.delivery_code:
            res = self.nacex_ws_getEstadoExpedicion()[0]
            # operations
            if res['errors']:
                _logger.info(res)
                self.action_error_update_state_expedition(res)
            else:
                # other_fields
                self.date = '%s-%s-%s' % (
                    res['return']['result']['fecha'].split('/')[2],
                    res['return']['result']['fecha'].split('/')[1],
                    res['return']['result']['fecha'].split('/')[0]
                )
                self.hour = res['return']['result']['hora']
                self.observations = res['return']['result']['observaciones']
                self.state_code = res['return']['result']['estado_code']
                res_estado = res['return']['result']['estado']
                # state
                state_old = self.state
                state_new = False
                if res_estado == "ERROR" or self.state_code == 18:
                    state_new = "error"
                elif res_estado or self.state_code in [9, 13, 17]:
                    state_new = "incidence"
                elif self.state_code in [1, 11, 12, 15]:
                    state_new = "shipped"
                elif self.state_code in [2, 3] \
                        or res_estado in ["REPARTO", "TRANSITO"]:
                    state_new = "in_transit"
                elif res_estado == "DELEGACION" or self.state_code == 16:
                    state_new = "in_delegation"
                elif self.state_code == 4 \
                        or res_estado in ["ENTREGADO", "OK", "SOL SIN OK"]:
                    state_new = "delivered"
                elif res_estado == "ANULADA":
                    state_new = "canceled"

                if state_new and state_new != state_old:
                    self.state = state_new

    @api.multi
    def nacex_ws_getEstadoExpedicion(self):
        # tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        # define
        delivery_code_split = self.delivery_code.split('/')
        # url
        url = "http://gprs.nacex.com/nacex_ws/ws?" \
              "method=getEstadoExpedicion&&user=%s&pass=%s" \
              "&data=origen=%s%7Calbaran=%s" \
              % (
                  nacex_username,
                  nacex_password,
                  delivery_code_split[0],
                  delivery_code_split[1]
              )
        b = StringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.FORBID_REUSE, 1)
        curl.setopt(pycurl.FRESH_CONNECT, 1)
        curl.setopt(pycurl.URL, url)
        curl.setopt(
            pycurl.USERAGENT,
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        )
        curl.setopt(
            pycurl.HTTPHEADER,
            ["Content-Type: text/xml; charset=utf-8"]
        )
        curl.perform()
        response = {
            'errors': True,
            'error': "",
            'return': ""
        }
        if curl.getinfo(pycurl.RESPONSE_CODE) == 200:
            response['errors'] = False
            response_curl = b.getvalue()
            response_curl_split = response_curl.split('|')
            if response_curl_split[0] == "ERROR":
                response['errors'] = True
            else:
                response['return'] = {
                    'label': ""
                }
                response['return']['result'] = {
                    'expe_codigo': response_curl_split[0],
                    'fecha': response_curl_split[1],
                    'hora': response_curl_split[2],
                    'observaciones': response_curl_split[3],
                    'estado': response_curl_split[4],
                    'estado_code': response_curl_split[5],
                    'origen': response_curl_split[6],
                    'albaran': response_curl_split[7]
                }
        else:
            response['error'] = b.getvalue()
            _logger.info('Response KO')
            _logger.info(pycurl.RESPONSE_CODE)
        # return
        return response
