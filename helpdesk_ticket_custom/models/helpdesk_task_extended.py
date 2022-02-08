# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se hereda el campo de ticket en el modelo de tareas
class helpdesk_task_extended(models.Model):
    _inherit = 'project.task'

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', help='Ticket this task was generated from')
