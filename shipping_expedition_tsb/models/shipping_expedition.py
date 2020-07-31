# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

import logging
import os
import ftplib
_logger = logging.getLogger(__name__)


class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    tsb_identiticket = fields.Char(
        string='Tsb Identiticket'
    )
    tsb_localizator = fields.Char(
        string='Tsb Localizator'
    )

    @api.multi
    def action_update_state(self):
        # operations
        for item in self:
            if item.carrier_id.carrier_type == 'tsb':
                item.action_update_state_tsb()
        # return
        return super(ShippingExpedition, self).action_update_state()

    @api.multi
    def action_update_state_tsb(self):
        for item in self:
            item.update_state_tsb()
        return False

    @api.multi
    def update_state_tsb(self):
        self.ensure_one()
        separator_fields = '|'
        # response
        response = {
            'errors': True,
            'error': "",
            'return': ""
        }
        # file_name ric
        file_name_real = "RIC_%s.txt" % self.carrier_id.tsb_sender_customer
        file_name = '%s/%s' % (
            os.path.dirname(os.path.abspath(__file__)),
            file_name_real
        )
        # ftp + download
        ftp = ftplib.FTP(self.carrier_id.tsb_ftp_host)
        ftp.login(
            self.carrier_id.tsb_ftp_user,
            self.carrier_id.tsb_ftp_password
        )
        ftp.cwd(self.carrier_id.tsb_ftp_directory_download)
        ls = []
        ftp.retrlines('MLSD', ls.append)
        shipping_expedition_find = False
        for entry in ls:
            entry_split = entry.split(";")
            entry_name = str(entry_split[4])
            entry_name = entry_name.replace(" ", "")
            if entry_name != "." and entry_name != "..":
                ftp.retrbinary(
                    "RETR "+entry_name,
                    open(file_name, 'wb').write
                )
                # read_file
                if os.path.isfile(file_name):
                    f = open(file_name, 'r')
                    for line in f:
                        if separator_fields in line:
                            line_split = line.split(separator_fields)
                            expedition_line = line_split[0]
                            reference_line = line_split[1]
                            origin_line = line_split[15]
                            ctrl_identiticket_line = line_split[28]
                            ctrl_localizator_line = line_split[29]
                            ctrl_link_line = line_split[30]
                            estd_fecha_llegada_line = line_split[33]
                            estd_codigo_sl = line_split[36]
                            if self.picking_id.name == reference_line \
                                    and not shipping_expedition_find:
                                estd_fll_split = estd_fecha_llegada_line.split(' ')
                                estd_fecha_llegada_line_real = '%s-%s-%s' % (
                                    estd_fll_split[0].split('/')[2],
                                    estd_fll_split[0].split('/')[1],
                                    estd_fll_split[0].split('/')[0]
                                )
                                self.code = expedition_line
                                self.delivery_code = reference_line
                                self.tsb_identiticket = ctrl_identiticket_line
                                self.date = estd_fecha_llegada_line_real
                                self.tsb_localizator = ctrl_localizator_line
                                self.url_info = ctrl_link_line
                                # codigo_situacion
                                if estd_codigo_sl != "00000001":
                                    # state_new
                                    if estd_codigo_sl == "00000002":
                                        state_new = "shipped"
                                    elif estd_codigo_sl in \
                                            ["00000003", "00000006"]:
                                        state_new = "in_transit"
                                    elif estd_codigo_sl == "00000004":
                                        state_new = "in_delegation"
                                    elif estd_codigo_sl == "00000005":
                                        state_new = "delivered"
                                    else:
                                        state_new = "incidence"
                                    # update_state
                                    if self.state != state_new:
                                        self.state = state_new
                                # result
                                response['return'] = {
                                    'label': ""
                                }
                                response['return']['result'] = {
                                    'expe_codigo': expedition_line,
                                    'fecha': estd_fecha_llegada_line_real,
                                    'estado_code': estd_codigo_sl,
                                    'origen': origin_line,
                                    'albaran': reference_line,
                                    'exps_rels': ""
                                }
                                shipping_expedition_find = True
        # response
        ftp.quit()
        response['errors'] = False
        return response
