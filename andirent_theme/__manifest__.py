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
        Launcher Andirent""",

    'description': """
        theme that adds andirent colors
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    'category': 'Web',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web_enterprise'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],

    'installable': True,
    'application': True,

    'assets': {
        # EXAMPLE Can include sub assets bundle
        'web.assets_backend': [
            ('replace', 'web_enterprise/static/src/legacy/scss/primary_variables.scss', 'andirent_theme/static/src/legacy/scss/primary_variables.scss'),
        ],
        'web._assets_common_styles': [
            ('replace', 'web_enterprise/static/src/legacy/scss/ui.scss', 'andirent_theme/static/src/legacy/scss/ui.scss'),
        ]
    },

    'license': 'LGPL-3',
    }

