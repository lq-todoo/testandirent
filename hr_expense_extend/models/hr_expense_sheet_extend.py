# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, Command, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense.sheet'

    identification_id = fields.Char(string='Nº identificación', related='employee_id.identification_id')