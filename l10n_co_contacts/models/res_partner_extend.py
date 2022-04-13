# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class l10n_co_contacts(models.Model):
    _inherit = 'res.partner'

    shareholding_structure = fields.Selection([('1', 'Accionista'),
                                               ('2', 'No Accionista')],
                                                string='Composición Accionaria',
                                                help='Indica si es accionista de la compañia, con una participación mayor al 10% ',
                                                required="True", store=True, default='2')

    share_percentage = fields.Float(string='% de participación',
                                    help='Establece el porcentaje de participación del accionista')






