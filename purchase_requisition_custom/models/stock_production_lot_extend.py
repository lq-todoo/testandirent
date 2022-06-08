from odoo import fields, models, api

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    plaque_id = fields.Many2one(comodel_name='stock_production_plaque', string='Placa')

    # Realaciona la placa/tarifa/fecha de contrato con numero de serie desde el modelo stock move line
    def compute_plaque_id(self):
        data = self.env['stock.move.line'].search([('lot_id', '=', self.ids),
                                                   ('product_id', '=', self.product_id.ids),
                                                   ('qty_done', '=', self.product_qty)], limit=1, order='id DESC')
        self.plaque_id = data.plaque_id.id





