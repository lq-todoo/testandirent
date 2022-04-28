from odoo import api, fields, models


class purchase_requisition_line_extend(models.Model):
    _inherit = 'stock.location'

    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse_id', store=True)
    location_id2 = fields.Many2one(comodel_name='location_warehouse', string='Locación', related='warehouse_id.location_id')
    show = fields.Boolean(related='warehouse_id.available_requisition')
    available_requisition = fields.Boolean(string='Puede usarse en requisiciones')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', string='Cuenta Analítica')




