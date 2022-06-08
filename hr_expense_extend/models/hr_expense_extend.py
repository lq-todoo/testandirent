# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, Command, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    identification_id = fields.Char(string='Nº identificación', related='employee_id.identification_id')
    code_analytic_account_id = fields.Char(string='codigo cuenta analítica', related='analytic_account_id.code')