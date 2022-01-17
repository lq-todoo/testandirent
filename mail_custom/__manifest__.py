# -*- coding: utf-8 -*-
{
    'name': "mail custom",

    'summary': """
        15.0.1  remove access create contacts in the field assigned to""",

    'description': """
        This customization modifies the permission of the mail base module
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'mail',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mail_activity_custom_view.xml',
    ],
}
