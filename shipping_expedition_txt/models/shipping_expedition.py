# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, _

import logging
from bs4 import BeautifulSoup
import requests
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def define_delegation_phone_txt(self):
        delegations_txt = {
            'A CORUÑA': {'phone': '981078907'},
            'ALBACETE': {'phone': '967213921', 'phone2': '967592544'},
            'ALCAÑIZ': {'phone': '978830655'},
            'ALGECIRAS': {'phone': '956698730'},
            'ALICANTE': {'phone': '965105294'},
            'ALMERIA': {'phone': '950315564'},
            'ARNEDO': {'phone': '941382806'},
            'AVILA': {'phone': '920213400'},
            'BARCELONA': {'phone': '936593776'},
            'BILBAO': {'phone': '944570066'},
            'BOROX': {'phone': '925527001'},
            'BURGOS': {'phone': '947484866'},
            'CACERES': {'phone': '924349243'},
            'CADIZ': {'phone': '902106836'},
            'CALATAYUD': {'phone': '976881206'},
            'CASTELLON': {'phone': '964204142'},
            'CIUDAD REAL': {'phone': '926274985'},
            'CORDOBA': {'phone': '957326068'},
            'CUENCA': {'phone': '969220154'},
            'GERONA': {'phone': '972477891'},
            'GRANADA': {'phone': '958491878'},
            'GUADALAJARA': {'phone': '949044023'},
            'HUELVA': {'phone': '959500193'},
            'HUESCA': {'phone': '974218946'},
            'IBIZA': {'phone': '971199932'},
            'LA CAROLINA': {'phone': '953681500'},
            'LEON': {'phone': '987269264'},
            'LISBOA': {'phone': '351210992094'},
            'LLEIDA': {'phone': '973257308'},
            'LOGROÑO': {'phone': '941257900'},
            'LUGO': {'phone': '982209158'},
            'MADRID': {'phone': '916878400'},
            'MADRIDEJOS': {'phone': '925245467'},
            'MALAGA': {'phone': '952179950', 'phone2': '952179951'},
            'MANRESA': {'phone': '938732770'},
            'MELILLA': {'phone': '952231130'},
            'MENORCA': {'phone': '971360834'},
            'MERIDA': {'phone': '924046212'},
            'MOLINA': {'phone': '968389160'},
            'NAVALMORAL': {'phone': '927538701'},
            'ORENSE': {'phone': '988256845'},
            'OVIEDO': {'phone': '985267730'},
            'PALENCIA': {'phone': '979043002'},
            'PALMA DE MALLORCA': {'phone': '971605097'},
            'PAMPLONA': {'phone': '948314381'},
            'PENDES': {'phone': '935169181'},
            'PONFERRADA': {'phone': '987419305'},
            'PUERTO DE SANTA MARIA': {'phone': '956858502'},
            'SAN SEBASTIAN': {'phone': '943377575'},
            'SALAMANCA': {'phone': '923250695'},
            'SANTANDER': {'phone': '942334422'},
            'SANTIAGO DE COMPOSTELA': {'phone': '981572341'},
            'SANTA CRUZ DE TENERIFE': {'phone': '922622640'},
            'SEGOVIA': {'phone': '921447152'},
            'SEVILLA': {'phone': '954260674'},
            'SORIA': {'phone': '975211477'},
            'TARRAGONA': {'phone': '977196871', 'phone2': '977196872'},
            'TERUEL': {'phone': '978605064'},
            'TORRIJOS': {'phone': '925761156'},
            'VALENCIA': {'phone': '961667593'},
            'VALLADOLID': {'phone': '983313876'},
            'VIC': {'phone': '938893217'},
            'VIGO': {'phone': '986488100'},
            'VITORIA': {'phone': '945292900'},
            'ZAMORA': {'phone': '980045035'},
            'ZARAGOZA': {'phone': '976144588'}
        }
        for item in self:
            if item.delegation_name and item.delegation_name != "":
                dns = str(item.delegation_name)
                # define
                web_base_url = self.env[
                    'ir.config_parameter'
                ].sudo().get_param('web.base.url')
                model_item = "shipping.expedition"
                url_item = "%s/web?#id=%s&view_type=form&model=%s" % (
                    web_base_url,
                    item.id,
                    model_item
                )
                # stranger_things
                if 'TORRIJOS' in dns:
                    dns = 'TORRIJOS'
                elif 'CIUDAD REAL' in dns:
                    dns = 'CIUDAD REAL'
                elif 'LEON' in dns:
                    dns = 'LEON'

                if dns == 'TENERIFE MARITIMO':
                    dns = 'SANTA CRUZ DE TENERIFE'

                if dns in delegations_txt:
                    item.delegation_phone = delegations_txt[dns]['phone']
                else:
                    # slack.message
                    attachments = [
                        {
                            "title": _('No se ha encontrado el telefono de '
                                       'TXT para la delegacion *%s*') % dns,
                            "color": "#ff0000",
                            "fallback": _("Ver expedicion %s") % url_item,
                            "actions": [
                                {
                                    "type": "button",
                                    "text": _("Ver expedicion"),
                                    "url": url_item
                                }
                            ]
                        }
                    ]
                    vals = {
                        'attachments': attachments,
                        'model': self._inherit,
                        'res_id': self.id,
                        'channel': self.env['ir.config_parameter'].sudo().get_param(
                            'slack_arelux_log_almacen_channel'
                        ),
                    }
                    self.env['slack.message'].sudo().create(vals)

    @api.multi
    def action_update_state(self):
        # operations
        for item in self:
            if item.carrier_id.carrier_type == 'txt':
                item.action_update_state_txt()
        # return
        return super(ShippingExpedition, self).action_update_state()

    @api.multi
    def action_update_state_txt(self):
        self.ensure_one()
        res = self.action_update_state_txt_real()[0]
        # operations
        if res['errors']:
            _logger.info(res)
            self.action_error_update_state_expedition(res)
        else:
            # fecha_entrega
            if 'fecha_entrega' in res['return']:
                if '/' in res['return']['fecha_entrega']:
                    res_fe = res['return']['fecha_entrega']
                    self.date = '%s-%s-%s' % (
                        res_fe.split('/')[2],
                        res_fe.split('/')[1],
                        res_fe.split('/')[0]
                    )
            # num_albaran
            if 'num_albaran' in res['return']:
                self.code = res['return']['num_albaran']
            # observaciones
            if 'observaciones' in res['return']:
                self.observations = res['return']['observaciones']
            # destino_expedicion1
            if 'destino_expedicion1' in res['return']:
                self.delegation_name = res['return']['destino_expedicion1']
                self.define_delegation_phone_txt()
            # state
            state_old = self.state
            state_new = False
            res_ee = res['return']['estado_expedicion']
            if res_ee == "ENTREGADO":
                state_new = "delivered"
            elif res_ee in ["EN REPARTO", "EN TRANSITO"]:
                state_new = "in_transit"
            elif res_ee in ["INCIDENCIA", "EN INCIDENCIA"]:
                state_new = "incidence"
            # state update
            if state_new and state_new != state_old:
                self.state = state_new

    @api.multi
    def action_update_state_txt_real(self):
        self.ensure_one()
        response = {
            'errors': True,
            'error': "Pendiente de realizar",
            'return': ""
        }
        page = requests.get(self.url_info)
        soup = BeautifulSoup(page.content, 'html.parser')
        eei = soup.find('input', {'id': 'TxtEstadoExpedicion'})
        if eei is not None:
            response['errors'] = False
            response['return'] = {}
            response['return']['estado_expedicion'] = eei.get('value')
            ee = response['return']['estado_expedicion']
            inputs = soup.find_all('input')
            for input_field in inputs:
                if input_field['id'] == 'TxtDestinoExpedicion1':
                    response['return'][
                        'destino_expedicion1'
                    ] = input_field['value']
                elif input_field['id'] == "TxtNumalbaran":
                    response['return'][
                        'num_albaran'
                    ] = input_field['value']
                elif input_field['id'] == "TxtEstadoExpedicion":
                    response['return'][
                        'estado_expedicion'
                    ] = input_field['value']
                elif input_field['id'] == "TxtFechaSalida":
                    response['return'][
                        'fecha_salida'
                    ] = input_field['value']
                elif input_field['id'] == "TxtFechaEntrega":
                    if ee == "ENTREGADO":
                        response['return'][
                            'fecha_entrega'
                        ] = input_field['value']
                elif input_field['id'] == "TxtObservaciones":
                    response['return'][
                        'observaciones'
                    ] = input_field['value']

            if 'num_albaran' not in response['return']:
                response['errors'] = True
        # return
        return response
