# -*- coding: utf-8 -*-
from odoo import models, fields, api

# Se crea modelo proyecto
class Project(models.Model):
    _inherit = "project.project"
    _description = 'Proyecto en mesa de ayuda'

    partner_project_id = fields.Many2many(comodel_name='res.partner', relation='x_project_project_res_partner_rel',
                                          column1='project_project_id', column2='res_partner_id', string='Compañias')
    current_location = fields.Many2one(comodel_name='project_location', string='Ubicación actual',
                                       help='Agregar la ciudad donde se encuentra la sede del cliente')
    # Concatenar     
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name + ' [ ' + str(rec.analytic_account_id.code) + ' ]'
            result.append((rec.id, name))
        return result
   




