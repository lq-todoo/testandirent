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
    'name': 'Expenses extend',
    'version': '0.1',
    'category': 'Human Resources/Expenses',
    'sequence': 70,
    'summary': 'Submit, validate and reinvoice employee expenses extend',
    'description': """

    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': 'https://www.andirent.co',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_views_extend.xml',
        'views/hr_expense_sheet_views_extend.xml',
        'report/hr_expense_report_extend.xml',
    ],
    'installable': True,
    'application': True,
}
