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
    'name': "andirent_theme",

    'summary': """
        15.0.2 the color navy blue, green and andirenmt background is added.
        15.1.0 The odoo icon is replaced by the andirent icon in desktop and mobile versions.
        15.1.1 background correction in mobile mode and burger menu color
    
        """,

    'description': """
        theme that adds andirent colors.
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    'category': 'Web',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'web_enterprise',
    ],

    'data': [
        'views/webclient_templates_custom.xml',
    ],

    'installable': True,
    'application': True,

    'assets': {
        'web._assets_common_styles': [
            ('replace', 'web_enterprise/static/src/legacy/scss/primary_variables.scss', 'andirent_theme/static/src/legacy/scss/primary_variables.scss'),
            ('replace', 'web_enterprise/static/src/legacy/scss/ui.scss', 'andirent_theme/static/src/legacy/scss/ui.scss'),
            # ('replace', 'web_enterprise/static/src/webclient/burger_menu/burger_menu.scss', 'andirent_theme/static/src/webclient/burger_menu/burger_menu.scss'),
        ],

        'web.assets_backend': [
            ('replace', 'web_enterprise/static/src/webclient/burger_menu/burger_menu.scss', 'andirent_theme/static/src/webclient/burger_menu/burger_menu.scss'),
        ]
    },

    'license': 'LGPL-3',
    }

