# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models, tools, _
from odoo.exceptions import Warning as UserError

import urllib
import pycurl
from io import StringIO
import xml.etree.ElementTree as ET

import logging
import base64
from PIL import Image

from datetime import datetime
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def generate_shipping_expedition(self):
        # operations
        for item in self:
            if item.carrier_id.carrier_type == 'nacex':
                item.generate_shipping_expedition_nacex()
        # return
        return super(StockPicking, self).generate_shipping_expedition()

    @api.multi
    def generate_shipping_expedition_nacex(self):
        self.ensure_one()
        if self.shipping_expedition_id.id == 0 \
                and self.carrier_id.carrier_type == 'nacex' \
                and self.partner_id:
            res = self.nacex_ws_putExpedicion()[0]
            # operations
            if res['errors']:
                # logger
                _logger.info(res)
                # action_error_create_expedition_message_slack
                self.action_error_create_expedition_message_slack({
                    'error': res['error']
                })
                # raise
                raise UserError(res['error'])
            else:
                # create
                vals = {
                    'picking_id': self.id,
                    'code': res['return']['result']['expe_codigo'],
                    'delivery_code': res['return']['result']['ag_cod_num_exp'],
                    'date': res['return']['result']['fecha_objetivo'],
                    'hour': res['return']['result']['hora_entrega'],
                    'origin': self.name,
                    'observations': res['return']['result']['cambios'],
                    'state': 'generate',
                    'state_code': 2
                }
                # url_info
                if '/' in vals['delivery_code']:
                    delivery_code_split = vals['delivery_code'].split("/")
                    if len(delivery_code_split) > 1:
                        vals['url_info'] = "http://www.nacex.es/" \
                                           "seguimientoDetalle.do?" \
                                           "agencia_origen=%s" \
                                           "&numero_albaran=%s" \
                                           "&estado=4&internacional=0" \
                                           "&externo=N" \
                                           "&usr=null&pas=null" % (
                            delivery_code_split[0],
                            delivery_code_split[1]
                        )
                # create
                if self.sale_id.user_id:
                    expedition_obj = self.env['shipping.expedition'].sudo(
                        self.sale_id.user_id.id
                    ).create(vals)
                else:
                    expedition_obj = self.env['shipping.expedition'].sudo().create(
                        vals
                    )
                # update
                self.shipping_expedition_id = expedition_obj.id
                # Fix
                self.action_view_etiqueta_item()

    @api.multi
    def nacex_ws_putExpedicion(self):
        self.ensure_one()
        # define
        today = datetime.today()
        datetime_body = today.strftime('%d/%m/%Y')
        # partner_name
        if self.partner_id.name:
            partner_name = self.partner_id.name
        else:
            partner_name = self.partner_id.parent_id.name
        #  Fix solicitud mal formada
        partner_name = partner_name.replace('&', '')
        # street2
        obs1 = ''
        obs2 = ''
        if self.partner_id.street2:
            street2_len = len(str(self.partner_id.street2))
            if street2_len <= 38:
                obs1 = self.partner_id.street2
            else:
                obs1 = self.partner_id.street2[0:38]
                obs2 = self.partner_id.street2[37:75].replace('&', '')
        # notes
        obs3 = ''
        obs4 = ''
        if self.shipping_expedition_note:
            note_len = len(str(self.shipping_expedition_note))
            if note_len > 1:
                if note_len <= 38:
                    obs3 = self.shipping_expedition_note
                else:
                    obs3 = self.shipping_expedition_note[0:38]
                    obs4 = self.shipping_expedition_note[37:75]
        # phone
        partner_picking_phone = ''
        if self.partner_id.mobile:
            partner_picking_phone = self.partner_id.mobile
        elif self.partner_id.phone:
            partner_picking_phone = self.partner_id.phone
        # tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        # tip_ser
        tip_ser = str(self.carrier_id.nacex_tip_ser)
        if self.partner_id.country_id.code not in ['ES', 'PT', 'AD']:
            tip_ser = str(self.carrier_id.nacex_tip_ser_int)
        # tip_ser (Baleares) 20 - NACEX MALLORCA MARÍTIMO
        if self.partner_id.country_id.code == 'ES' \
                and self.partner_id.state_id.code == 'PM':
            tip_ser = '20'
        # tip_env
        tip_env = str(self.carrier_id.nacex_tip_env)
        if self.partner_id.country_id.code not in ['ES', 'PT', 'AD']:
            tip_env = str(self.carrier_id.nacex_tip_env_int)
        # create
        url = "http://gprs.nacex.com/nacex_ws/soap"
        body = """<soapenv:Envelope xmlns:soapenv="%s" xmlns:typ="urn:soap/types">
        <soapenv:Header/>
        <soapenv:Body>
        <typ:putExpedicion>
        <String_1>%s</String_1>
        <String_2>"%s</String_2>
        <arrayOfString_3>del_cli=%s</arrayOfString_3>
        <arrayOfString_3>num_cli=%s</arrayOfString_3>
        <arrayOfString_3>fec=%s</arrayOfString_3>
        <arrayOfString_3>dep_cli=%s</arrayOfString_3>
        <arrayOfString_3>tip_ser=%s</arrayOfString_3>
        <arrayOfString_3>tip_cob=%s</arrayOfString_3>
        <arrayOfString_3>tip_env=%s</arrayOfString_3>
        <arrayOfString_3>obs1=%s</arrayOfString_3>
        <arrayOfString_3>obs2=%s</arrayOfString_3>
        <arrayOfString_3>obs3=%s</arrayOfString_3>
        <arrayOfString_3>obs4=%s</arrayOfString_3>
        <arrayOfString_3>ref_cli=%s</arrayOfString_3>
        <arrayOfString_3>bul=%s</arrayOfString_3>
        <arrayOfString_3>kil=%s</arrayOfString_3>
        <arrayOfString_3>nom_rec=%s</arrayOfString_3>
        <arrayOfString_3>dir_rec=%s</arrayOfString_3>
        <arrayOfString_3>cp_rec=%s</arrayOfString_3>
        <arrayOfString_3>pob_rec=%s</arrayOfString_3>
        <arrayOfString_3>tel_rec=%s</arrayOfString_3>
        <arrayOfString_3>nom_ent=%s</arrayOfString_3>
        <arrayOfString_3>per_ent=%s</arrayOfString_3>
        <arrayOfString_3>dir_ent=%s</arrayOfString_3>
        <arrayOfString_3>pais_ent=%s</arrayOfString_3>
        <arrayOfString_3>cp_ent=%s</arrayOfString_3>
        <arrayOfString_3>pob_ent=%s</arrayOfString_3>
        <arrayOfString_3>tel_ent=%s</arrayOfString_3>""" % (
            "http://schemas.xmlsoap.org/soap/envelope/",
            nacex_username,  # String_1
            nacex_password,  # String_2
            self.carrier_id.nacex_del_cli,  # del_cli
            self.carrier_id.nacex_num_cli,  # num_cli
            datetime_body,  # fec
            self.carrier_id.nacex_dep_cli,  # dep_cli
            tip_ser,  # tip_ser
            self.carrier_id.nacex_tip_cob,  # tip_cob
            tip_env,  # tip_env
            obs1,  # obs1
            obs2,  # obs2
            obs3,  # obs3
            obs4,  # obs4
            self.name,  # ref_cli
            1,  # bul
            self.weight,  # kil,
            self.company_id.website,  # nom_rec
            self.company_id.street[0:60],  # dir_rec
            self.company_id.zip,  # cp_rec
            self.company_id.city[0:39],  # pob_rec
            self.company_id.phone,  # tel_rec
            partner_name[0:50],  # nom_ent
            partner_name[0:35],  # per_ent
            self.partner_id.street[0:60],  # dir_ent
            self.partner_id.country_id.code,  # pais_ent
            self.partner_id.zip,  # cp_ent
            self.partner_id.city[0:39],  # pob_ent
            partner_picking_phone,  # tel_ent
        )
        # con
        if self.partner_id.country_id.code not in [
            'ES', 'PT', 'AD'
        ]:
            # con
            con = ''
            for product_id in self.pack_operation_product_ids:
                if product_id.product_id:
                    con = '%s%s,' % (
                        con,
                        product_id.product_id.name
                    )
            # val_dec
            val_dec = "0.0"
            if self.sale_id:
                val_dec = self.sale_id.amount_total
            # body
            body += """
            <arrayOfString_3>con=%s</arrayOfString_3>
            <arrayOfString_3>val_dec=%s</arrayOfString_3>""" % (
                con[0:80],
                val_dec
            )
        # prealerta
        if self.partner_id.mobile:
            body += """
            <arrayOfString_3>tip_pre1=S</arrayOfString_3>
            <arrayOfString_3>mod_pre1=S</arrayOfString_3>
            <arrayOfString_3>pre1=%s</arrayOfString_3>""" % self.partner_id.mobile
        # final
        body += """
        </typ:putExpedicion>
        </soapenv:Body>
        </soapenv:Envelope>"""
        b = StringIO.StringIO()
        # continue
        curl = pycurl.Curl()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.FORBID_REUSE, 1)
        curl.setopt(pycurl.FRESH_CONNECT, 1)
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.POSTFIELDS, body)
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
            root = ET.fromstring(response_curl)
            response['return'] = {
                'label': "",
                'results': []
            }
            for item in root.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                for item2 in item.findall('{urn:soap/types}putExpedicionResponse'):
                    for result in item2.findall('result'):
                        response['return']['results'].append(result.text)

            if response['return']['results'][0] == "ERROR":
                response['errors'] = True
                response['error'] = response['return']['results'][1]
            else:
                response['return']['result'] = {
                    'expe_codigo':
                        response['return']['results'][0],
                    'ag_cod_num_exp':
                        response['return']['results'][1],
                    'color': response['return']['results'][2],
                    'ent_ruta': response['return']['results'][3],
                    'ent_cod': response['return']['results'][4],
                    'ent_nom': response['return']['results'][5],
                    'ent_tlf': response['return']['results'][6],
                    'serv': response['return']['results'][7],
                    'hora_entrega':
                        response['return']['results'][8],
                    'barcode': response['return']['results'][9],
                    'fecha_objetivo':
                        datetime.strptime(
                            response['return']['results'][10],
                            "%d/%m/%Y"
                        ).date(),
                    'cambios': response['return']['results'][11],
                    'origin': self.name
                }
        else:
            response['error'] = b.getvalue()
            _logger.info('Response KO')
            _logger.info(pycurl.RESPONSE_CODE)
            response_curl = b.getvalue()
            root = ET.fromstring(response_curl)
            _logger.info(response_curl)
            response['errors'] = True
            response['return'] = {
                'label': "",
                'results': []
            }
            for item in root.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                for item2 in item.findall('{urn:soap/types}putExpedicionResponse'):
                    for result in item2.findall('result'):
                        response['return']['results'].append(result.text)
            # Fix
            if len(response['return']['results']) > 0:
                if response['return']['results'][0] == "ERROR":
                    response['error'] = response['return']['results'][1]
            # log
            _logger.info(body)
        # return
        return response

    @api.multi
    def view_etiqueta_nacex(self):
        self.ensure_one()
        # url
        url = "http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta" \
              "&user=%s&pass=%s&data=ag=%s%7Cnumero=%s%7Cmodelo=IMAGEN_B" \
              % (
                  tools.config.get('nacex_username'),
                  tools.config.get('nacex_password'),
                  self.shipping_expedition_id.delivery_code.split('/')[0],
                  self.shipping_expedition_id.delivery_code.split('/')[1]
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
            'return': "",
            'return_real': "",
        }
        if curl.getinfo(pycurl.RESPONSE_CODE) == 200:
            response_curl = b.getvalue()
            response_curl_split = response_curl.split('|')
            if response_curl_split[0] != "ERROR":
                response['return_real'] = response_curl
                edits = [('-', '+'), ('_', '/'), ('*', '=')]
                for search, replace in edits:
                    response_curl = response_curl.replace(search, replace)

                response_curl = response_curl.decode('base64')
                response['errors'] = False
                response['return'] = response_curl
        else:
            response = {
                'errors': True,
                'error':
                    _("No se puede generar la etiqueta de una expedicion "
                      "que no esta creada todavia"),
                'return_real': ""
            }
        # return
        return response

    @api.multi
    def action_view_etiqueta_item(self):
        self.ensure_one()
        if self.shipping_expedition_id:
            res = self.view_etiqueta_nacex()[0]
            if res['errors']:
                raise exceptions.Warning(res['error'])
            else:
                # vals
                vals = {
                    'name': "%s-%s.png" % (
                        self.shipping_expedition_id.delivery_code.split('/')[0],
                        self.shipping_expedition_id.delivery_code.split('/')[1]
                    ),
                    'datas': base64.encodestring(res['return']),
                    'datas_fname': "%s-%s.png" % (
                        self.shipping_expedition_id.delivery_code.split('/')[0],
                        self.shipping_expedition_id.delivery_code.split('/')[1]
                    ),
                    'res_model': 'stock.picking',
                    'res_id': self.id
                }
                ir_attachment_obj = self.env['ir.attachment'].sudo().create(vals)
                self.ir_attachment_id = ir_attachment_obj.id

    @api.multi
    def action_view_etiqueta(self, package_ids=None):
        for obj in self:
            if obj.shipping_expedition_id:
                obj.action_view_etiqueta_item()

    @api.multi
    def _get_expedition_image(self):
        # operations
        self.ensure_one()
        url_ie = "http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta&user=%s" \
                 "&pass=%s&data=codexp=%s|modelo=IMAGEN" \
                 % (
                     tools.config.get('nacex_username'),
                     tools.config.get('nacex_password'),
                     self.shipping_expedition_id.code
                 )

        if self.shipping_expedition_id:
            if self.carrier_id.carrier_type == 'nacex':
                # return url_image_expedition
                file = StringIO(
                    urllib.urlopen(url_ie).read()
                )
                img = Image.open(file)
                return img

    @api.multi
    def _get_expedition_image_url_ir_attachment(self):
        self.ensure_one()
        if self.shipping_expedition_id:
            if self.carrier_id.carrier_type == 'nacex':
                ir_attachment_ids = self.env['ir.attachment'].search(
                    [
                        ('res_model', '=', 'stock.picking'),
                        ('res_id', '=', self.id)
                    ]
                )
                return_url = ''
                for ir_attachment_id in ir_attachment_ids:
                    return_url = '/web/image/%s' % ir_attachment_id.id

                return return_url
