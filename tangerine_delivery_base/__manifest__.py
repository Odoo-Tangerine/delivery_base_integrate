# -*- coding: utf-8 -*-
{
    'name': 'Shipping Methods Base',
    'summary': """""",
    'author': 'Long Duong Nhat',
    'category': 'Inventory/Delivery',
    'support': 'odoo.tangerine@gmail.com',
    'version': '17.0.1.0',
    'depends': [
        'mail',
        'base',
        'delivery',
        'sale_management',
        'stock_delivery',
        'sale_service',
        'stock',
        'purchase',
        'tangerine_address_vn',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_data.xml',
        'views/delivery_base_views.xml',
        'views/delivery_route_api_views.xml',
        'views/delivery_status_views.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml'
    ],
    'images': ['static/description/thumbnail.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False
}