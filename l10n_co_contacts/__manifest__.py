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
    'name': "contacts extend",

    'summary': """
        15.0.1 fields required by Sagrilaft are added""",

    'description': """
        Add options and required fields for Colombian localization
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contacts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_partner_extend_view.xml',
    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
