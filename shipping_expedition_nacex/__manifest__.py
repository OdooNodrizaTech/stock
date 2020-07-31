# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shipping Expedition Nacex",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT), "
              "Odoo Community Association (OCA)",
    "website": "https://nodrizatech.com/",
    "category": "Delivery",
    "license": "AGPL-3",
    "depends": [
        "shipping_expedition",
        "sale",
        "sale_stock"
    ],
    "external_dependencies": {
        "python": [
            "suds",
            "pycurl",
            "PIL"
        ],
    },
    "data": [
        "views/delivery_carrier_view.xml",
        "views/stock_picking_view.xml",
        "views/shipping_expedition_view.xml",
        "report/shipping_expedition_views.xml",
        "report/report_nacex.xml",
    ],
    "installable": True
}
