from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    stock_quant = fields.One2many(comodel_name='stock.quant', inverse_name='product_tmpl_id',
                                  string='Inventario disponible')


