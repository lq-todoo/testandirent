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
    'name': "helpdesk ticket custom",

    'summary': """
        This module creates new models and fields to extend the functionality of the helpdesk tickets,
        and website tickets form
        """,

    'description': """
        Module that extends functionality in the helpdesk module and add website tickets form
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'helpdesk',
    'version': '15.1.2',

    # any module necessary for this one to work correctly
    'depends': [
                'helpdesk',
                'industry_fsm',
                'website_helpdesk_form',
                'contacts',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views_helpdesk_classification.xml',
        'views/views_helpdesk_family.xml',
        'views/views_helpdesk_project.xml',
        'views/views_helpdesk_sub_group.xml',
        'views/views_helpdesk_task_extended.xml',
        'views/views_helpdesk_team_extended.xml',
        'views/views_helpdesk_ticket_extended.xml',
        'views/views_helpdesk_partner_extended.xml',
        'views/views_helpdesk_users_extended.xml',
        'views/views_toggle_ticket_show.xml',
        'views/helpdesk_templates_o.xml',
        'data/automation.xml',
        #'views/assets.xml',
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_frontend': [
            'helpdesk_ticket_custom/static/src/js/script.js',
        ],
        'website.assets_editor': [
            'helpdesk_ticket_custom/static/src/js/website_helpdesk_form_editor.js',
        ],
    },

    'installable': True,
}
