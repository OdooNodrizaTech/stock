# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shipping expedition",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Delivery",
    "license": "AGPL-3",
    "depends": [
        "base",
        "delivery",
        "stock",
        "cashondelivery",  # https://github.com/OdooNodrizaTech/sale
        "sale_stock"
    ],
    "data": [
        "data/ir_cron.xml",
        "views/delivery_carrier_view.xml",
        "views/shipping_expedition_view.xml",
        "views/res_partner_view.xml",
        "views/crm_lead_view.xml",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True
}
