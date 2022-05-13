from odoo import fields, models, api, exceptions

class Productionplaque(models.Model):
    _name = 'stock_production_plaque'

    name = fields.Char(string='Plaque', required=True, help="Unique Plaque", index=True)
    ref = fields.Char('Internal Reference', help="Internal reference number in case it differs from the manufacturer's plaque number")

    # SQL constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La placa ya existe'),
    ]