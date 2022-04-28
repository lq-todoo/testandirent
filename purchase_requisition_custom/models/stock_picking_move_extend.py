from odoo import fields, models, api


class stock_picking_extend(models.Model):
    _inherit = 'stock.move'

    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', string='Cuenta Analítica',
                                          related='location_dest_id.account_analytic_id')
    standard_price = fields.Float(
        string='Costo Unitario', company_dependent=True,
        digits='Product Price',
        groups="base.group_user",
        related='product_id.standard_price',
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
            In FIFO: value of the last unit that left the stock (automatically computed).
            Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
            Used to compute margins on sale orders.""")

    standard_price_t = fields.Float(
        string='Costo',
        compute='_compute_standard_price_t',
        help="""Costo unitario por cantidad de productos."""
    )

    # Optiene el costo subtotal
    @api.depends('standard_price')
    def _compute_standard_price_t(self):
        for rec in self:
            rec.standard_price_t = rec.standard_price*rec.product_uom_qty


