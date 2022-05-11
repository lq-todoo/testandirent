from odoo import fields, models, api


class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    plaque_id = fields.Many2one(comodel_name='stock_production_plaque', related='product_id.stock_quant.plaque_id',
                                string='Placa', index=True, ondelete='restrict',
                                domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]")



