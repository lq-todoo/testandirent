# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# Desarrollador y funcional Odoo
# Github: jotate70
# Cel. +57 3147754740
#
#

{
    'name': "Purchase Agreements Custom",

    'summary': """
        15.0.1 module that adds approvals by levels according to the budget of each immediate boss in the purchase requisitions.
        15.1.0 the option to assign stock picking tasks to warehouse managers will be added
        15.2.0 ticket relationship with requisitions is added
        15.2.1 Restrictions are added in fields
        15.3.0 This versions contains stock movement in two steps, origin location to transit location, transit location to destination location. 
        """,

    'description': """
        module that adds approvals by levels according to the budget of each immediate boss in the purchase requisitions.
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition',
                'hr_holidays',
                'purchase_stock',
                'stock',
                'sale_stock',
                'helpdesk',
                'web_domain_field',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_extend_view.xml',
        'views/purchase_extend_view.xml',
        'views/purchase_requisition_extend_view.xml',
        'views/purchase_requisition_line_extend_view.xml',
        'views/users_extend_view.xml',
        'views/stock_picking_extend_view.xml',
        'views/product_template_extend_view.xml',
        'views/helpdesk_ticket_extended_view.xml',
        'views/stock_warehouse_extend_view.xml',
        'views/stock_location_form_extend_view.xml',
        'views/location_warehouse_view.xml',
        'views/stock_picking_move_extend_view.xml',
        'views/stock_picking_type_extend_view.xml',
        'views/account_analytic_line_extend_view.xml',
        'views/stock_quant_custom_view.xml',
    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',

}
