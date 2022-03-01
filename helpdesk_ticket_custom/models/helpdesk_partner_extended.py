# -*- coding: utf-8 -*-
import io
import base64
from odoo import models, fields, api


# heredamos del modelo usuarios
class helpdesk_partner_extended(models.Model):
    _inherit = 'res.partner'

    x_ticket_show = fields.Boolean(string='Mostrar en tickets',
                                   help='Este boton permite mostrar el contacto en los tickets')

    x_project = fields.Many2many(comodel_name='helpdesk_project',
                                 relation='x_helpdesk_project_res_partner_rel',
                                 column1='res_partner_id',
                                 column2='helpdesk_project_id',
                                 string='Proyecto',
                                 )

    # Se aplica un decorador que detecta el cambio
    @api.onchange('x_ticket_show', 'x_project', 'edit_records')
    def _domain_onchange_x_project(self):
        if self.is_company == False:
            return {'domain': {'x_project': [('partner_id', 'in', self.parent_id.ids)]}}



















