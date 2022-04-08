# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json

class employee_extend(models.Model):
    _inherit = 'hr.employee'

    active_budget = fields.Boolean(string='Es responsable de presupuesto',
                                   help='Está check activa la opción de asignar presupiesto al empleado')
    general_manager = fields.Boolean(string='Sin tope de presupuesto',
                                     help='Es la persona que no tiene limite para aprobar presupuesto')
    budget = fields.Float(string='Presupuesto', help='Monto maximo que puede aprobar por solicitud de compra')
    manager_warehouse = fields.Many2many(comodel_name='stock.warehouse', relation='x_hr_employee_stock_warehouse_rel',
                                         column1='hr_employee_id', column2='stock_warehouse_id', string='Almacenes',
                                         help='Almacenes que puedes aprobar transferencia internas inmeditas')

    stock_warehouse_domain = fields.Char(compute="_compute_stock_warehouse", readonly=True, store=False)

    # Función que aplica filtro dinamico de almacen
    @api.depends('manager_warehouse')
    def _compute_stock_warehouse(self):
        warehouse = self.env['stock.warehouse'].sudo().search([('employee_id', "=", False)])
        for rec in self:
            rec.stock_warehouse_domain = json.dumps(
                [('id', "=", warehouse.ids)]
            )





