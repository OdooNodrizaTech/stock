# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    s3_upload = fields.Boolean(
        string='S3 Upload'
    )
    s3_bucket = fields.Char(
        string='S3 Bucket'
    )
    s3_folder = fields.Char(
        string='S3 Folder'
    )
