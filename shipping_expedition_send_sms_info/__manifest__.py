# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shipping Expedition Send Sms Info",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Delivery",
    "license": "AGPL-3",
    "depends": [
        "delivery",
        "shipping_expedition",
        "aws_sms_shipping_expedition"  # https://github.com/OdooNodrizaTech/sms
    ],
    "data": [
        "data/ir_cron.xml",
        "views/delivery_carrier_view.xml"
    ],
    'installable': True
}
