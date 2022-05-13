from odoo import fields, models, api


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    plaque_id = fields.Char(string='Placa')



