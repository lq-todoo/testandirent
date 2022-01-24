# -*- coding: utf-8 -*-
{
    'name': "mail custom",

    'summary': """
        15.0.1  remove access create contacts in the field assigned to
        15.0.2  Option to edit and delete notes is disabled
        """,


    'description': """
        This customization modifies the permission of the mail base module
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'mail',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mail_activity_custom_view.xml',
    ],

    'installable': True,
    'application': True,

    # only loaded in demonstration mode
    'assets': {
        'web.assets_qweb': [
            # EXAMPLE: Add everyithing in the folder
            'mail_custom/static/src/components/message_action_list/message_action_list_custom.xml',
            # EXAMPLE: Remove every .xml file
            ('remove', 'mail/static/src/components/message_action_list/message_action_list.xml'),
        ],

    },

    'license': 'LGPL-3',
}
