# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from lxml import etree

# heredamos del modelo helpdesk team
class helpdesk_team_extended(models.Model):
    _inherit = 'helpdesk.team'

    x_visibility = fields.Boolean(string='Visibilidad de clasificación', help='Permite mostrar el campo clasificación en los ticket')
    #
    # def init(self):
    #     teams = self.env['helpdesk.team'].sudo().search([])
    #     default_form = etree.fromstring(self.env.ref('helpdesk_ticket_custom.website_helpdesk_form_ticket_submit_form_inherit').arch)
    #     if teams:
    #         for t in teams:
    #             xmlid = 'website_helpdesk_form.team_form_' + str(t.id)
    #             ir = self.env['ir.ui.view'].sudo().search([('name','=',xmlid)])
    #             if ir:
    #                 ir.write({'arch': etree.tostring(default_form)})
