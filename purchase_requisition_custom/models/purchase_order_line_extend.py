from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    image_product = fields.Binary(string='Imagen', related='product_id.image_1920')
