# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class l10n_co_contacts(models.Model):
    _inherit = 'res.partner'

    # demo = fields.Char()
    # tax_auditor = fields.Many2one(comodel_name='res.partner', string='Auditor', help='Auditor a cargo')

    # auditor_document_type = fields.Many2one(comodel_name='l10n_latam.identification.type', string='Tipo de documento',
    #                                         help='Tipo de documento')

    # auditor_document = fields.Char(string='Documento', related='tax_auditor.vat',
    #                                help='Documento del revisor fiscal a cargo en la compañia')
    # accountant = fields.Many2one(comodel_name='res.partner', string='Contador', help='Contador a cargo')
    # accountant_document_type = fields.Many2one(comodel_name='l10n_latam.identification.type', string='Tipo de documento',
    #                                         help='Tipo de documento',
    #                                         compute='_get_document_type2')
    # accountant_document = fields.Char(string='Documento',
    #                                   related='accountant.vat', help='Documento de contador a cargo')
    #
    # auditor document type
    # @api.depends('tax_auditor')
    # def _get_document_type(self):
    #     if self.tax_auditor:
    #         self.auditor_document_type = self.tax_auditor.l10n_latam_identification_type_id
    #     else:
    #         self.auditor_document_type = False
    #



