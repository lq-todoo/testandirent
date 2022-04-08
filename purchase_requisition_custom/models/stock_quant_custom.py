from odoo import fields, models, api

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    name = fields.Char()
