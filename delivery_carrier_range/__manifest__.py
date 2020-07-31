# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Delivery Carrier Range",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "base",
        "crm",
        "stock",
        "delivery"
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/product_template_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True
}
