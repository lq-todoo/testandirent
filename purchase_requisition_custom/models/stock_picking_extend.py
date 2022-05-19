from odoo import fields, models, api
from odoo.exceptions import UserError

class stock_picking_extend(models.Model):
    _inherit = 'stock.picking'

    requisition_id = fields.Many2one(comodel_name='purchase.requisition', string='Acuerdos de compra')
    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')],
                            'Operación', related='picking_type_id.code')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='A almacén', related='location_dest_id.warehouse_id')
    activity_id = fields.Integer(string='id actividad')     # id de la actividad asignada
    ticket_many2many = fields.Many2many(comodel_name='helpdesk.ticket',
                                        relation='x_helpdesk_ticket_purchase_requisition_rel',
                                        column1='purchase_requisition_id', column2='helpdesk_ticket_id',
                                        string='Tickets', related='requisition_id.ticket_many2many')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', string='Cuenta Analítica',
                                          related='location_dest_id.account_analytic_id', store=True)
    stage = fields.Integer(string='Etapa')
    validation = fields.Integer(string='Validacación', help='Permite validar el stock picking de transito a destino')
    parent_stock_picking = fields.Many2one(comodel_name='stock.picking', string='Stock picking padre')
    signature_receives = fields.Binary(string='Recibe')
    employee_receives_id = fields.Many2one(comodel_name='hr.employee', string='Nombre', store=True)
    employee_receives_job_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo', store=True,
                                               related='employee_receives_id.job_id')
    signature_delivery = fields.Binary(string='Entrega')
    employee_delivery_id = fields.Many2one(comodel_name='hr.employee', string='Nombre', store=True)
    employee_delivery_job_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo', store=True,
                                               related='employee_delivery_id.job_id')
    signature_warehouse_manager = fields.Binary(string='Responsable de almacen')
    employee_warehouse_id = fields.Many2one(comodel_name='hr.employee', string='Nombre', store=True)
    employee_warehouse_job_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo', store=True,
                                               related='employee_warehouse_id.job_id')
    x_type_id = fields.Many2one(comodel_name='purchase_requisition_custom_stock_picking_type',
                                string='Tipo', help='Indica el tipo de tranferencia de inventario')

    # Selecciona el empleado responsable de bodega
    @api.onchange('signature_warehouse_manager')
    def selection_warehouse_manager(self):
        self.write({'employee_warehouse_id': self.env.user.employee_id})

    # Selecciona el empleado que firma como responsable de entrega
    @api.onchange('signature_delivery')
    def selection_delivery(self):
        self.write({'employee_delivery_id': self.env.user.employee_id})

    # Selecciona el empleado que firma como responsable de entrega
    @api.onchange('signature_receives')
    def selection_receives(self):
        self.write({'employee_receives_id': self.env.user.employee_id})

    # Se crea apunte analítico
    def compute_account_analytic_cost(self):
        # Condición para solo registrar apuntes analiticos donde no existe ordenes de compra y venta
        if self.purchase_id:
            return True
        elif self.sale_id:
            return True
        else:
            # Permite determinar si el importe es negativo o positivo (debita/acredita) mediante el tipo de operación
            if self.code == 'internal':
                a = 1
            elif self.code == 'outgoing':
                a = 1
            elif self.code == 'incoming':
                a = -1
            # Crea apunte analítico
            for rec in self.move_ids_without_package:
                create_account_analytic = {
                    'name': rec.description_picking,
                    'account_id': rec.account_analytic_id.id,
                    'partner_id': self.partner_id.id,
                    'date': fields.datetime.now(),
                    'company_id': self.env.company.id,
                    'amount': rec.standard_price_t*a,
                    'unit_amount': rec.product_uom_qty,
                    'product_id': rec.product_id.id,
                    'product_uom_id': rec.product_uom.id,
                    'stock_picking_line_id': rec.id,
                }
                self.env['account.analytic.line'].sudo().create(create_account_analytic)

    # Actualización de la función del boton como por hacer
    def action_confirm(self):
        if self.parent_stock_picking:
            if self.parent_stock_picking.stage == 1 and self.parent_stock_picking.state == 'done':
                self._check_company()
                self.mapped('package_level_ids').filtered(
                    lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
                # call `_action_confirm` on every draft move
                self.mapped('move_lines') \
                    .filtered(lambda move: move.state == 'draft') \
                    ._action_confirm()

                # run scheduler for moves forecasted to not have enough in stock
                self.mapped('move_lines').filtered(
                    lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()

                #  Marca actividad como hecha de forma automatica
                new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                new_activity.action_feedback(feedback='Es confirmada')
                return True
            else:
                raise UserError('Debe terminar primero la transferencia de ubicación origen a transito.')
        else:
            self._check_company()
            self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
            # call `_action_confirm` on every draft move
            self.mapped('move_lines')\
                .filtered(lambda move: move.state == 'draft')\
                ._action_confirm()

            # run scheduler for moves forecasted to not have enough in stock
            self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()

            #  Marca actividad como hecha de forma automatica
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es confirmada')
            return True

