from odoo import fields, models, api
from odoo.exceptions import UserError

class stock_warehouse_extend(models.Model):
    _inherit = 'stock.warehouse'

    employee_id = fields.Many2many(comodel_name='hr.employee', relation='x_hr_employee_stock_warehouse_rel',
                     column1='stock_warehouse_id', column2='hr_employee_id', string='Empleado responsable',
                     help='Empleado que puede aprobar transferencias internas en el almacen')

    # validación limite para asociar almacen
    @api.onchange('employee_id')
    def _compute_ticket_limit(self):
        c = 0
        for rec in self.employee_id:
            c = c + 1
            if c > 1:
                raise UserError('Solo puede asociar un usuario por almacen')

