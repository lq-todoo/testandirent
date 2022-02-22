# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# heredamos del modelo de tickets de mesa ayuda
class helpdesk_ticket_extended(models.Model):
    _inherit = 'helpdesk.ticket'

    x_visibility_related = fields.Boolean(string='Campo oculto', related='team_id.x_visibility', store=True,
                                          readonly=True)
    x_classification = fields.Many2one(comodel_name='helpdesk_classification', string='Clasificación')
    x_project = fields.Many2one(comodel_name='helpdesk_project', string='Proyecto', required="True",
                                help='El proyecto está relacionado con su respectivo centro de costo')
    x_family = fields.Many2one(comodel_name='helpdesk_family', string='Familia', required="True",
                               help='Familia a la que pertenece el requerimiento del ticket')
    x_sub_group = fields.Many2one(comodel_name='helpdesk_sub_group', string='Sub grupo', required="True",
                                  help='Subgrupo relacionado a cada familia')
    current_location = fields.Char(string='Ubicación del proyecto', related='x_project.current_location', store=True,
                                   help='Indica la ubicación del proyecto')
    location = fields.Selection([('Bogotá', 'Bogotá'),
                                 ('Medellín', 'Medellín'),
                                 ('Barranquilla', 'Barranquilla'),
                                 ],
                                string='Locación', help='Indica la ciudad donde se ejecuta el proyecto', store=True)

    ticket_type = fields.Selection([('1', 'Ticket Interno'),
                                    ('2', 'Ticket Externo')],
                                   string='Tipo de ticket',
                                   help='Permite definir si es un ticket interno o un ticket desde el sitio web',
                                   required="True", store=True, default='2')

    # Se aplica un decorador que detecta el cambio del campo partner_id
    @api.onchange('partner_id')
    def _domain_ochange_x_partner(self):
        return {'domain': {'x_project': [('partner_id', "=", self.partner_id.id)]}}

    # Se aplica un decorador que detecta el cambio del campo x_familia
    @api.onchange('x_family')
    def _domain_ochange_x_familia(self):
        return{'domain': {'x_sub_group': [('x_family', "=", self.x_family.id)]}}












