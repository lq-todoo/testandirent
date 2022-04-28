from odoo import fields, models, api
from odoo.exceptions import UserError

class stock_warehouse_extend(models.Model):
    _inherit = 'stock.warehouse'

    employee_id = fields.Many2many(comodel_name='hr.employee', relation='x_hr_employee_stock_warehouse_rel',
                     column1='stock_warehouse_id', column2='hr_employee_id', string='Empleado responsable',
                     help='Empleado que puede aprobar transferencias internas en el almacen')

    location_id = fields.Many2one(comodel_name="location_warehouse", string='Locación', help="Indica la locación/ciudad donde se encuentra el almacen")

    available_requisition = fields.Boolean(string='Puede usarse en requisiciones')

    code = fields.Char('Short Name', required=True, size=8, help="Short name used to identify your warehouse")

    # validación limite para asociar almacen
    @api.onchange('employee_id')
    def _compute_ticket_limit(self):
        c = 0
        for rec in self.employee_id:
            c = c + 1
            if c > 1:
                raise UserError('Solo puede asociar un usuario por almacen')

