from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

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
    contract_date = fields.Date(string='Inicio de contrato',
                                help='Indica la fecha que se realiza el contrato asociada a dicha transferencia')
    contract_date_end = fields.Date(string='Finalización de contrato',
                                    help='Indica la fecha que se realiza el contrato asociada a dicha transferencia')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda', required=True)

    # seleciona divisa por defecto
    @api.onchange('picking_type_id')
    def _selection_currency_id_default(self):
        self.write({'currency_id': self.env.company.currency_id})

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

    # Se crea apuntes analítico
    def compute_account_analytic_cost(self):
        if self.account_analytic_id:
            # Multi moneda
            monetary = self.env['res.currency'].search([('id', '=', self.currency_id.ids)],
                                                            order='id DESC', limit=1)
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
                # Crea apunte analítico a mover
                for rec in self.move_ids_without_package:
                    create_account_analytic = {
                        'name': rec.description_picking,
                        'account_id': rec.account_analytic_id.id,
                        'partner_id': self.partner_id.id,
                        'date': fields.datetime.now(),
                        'company_id': self.env.company.id,
                        'amount': (rec.standard_price_t*a)/monetary.rate,
                        'unit_amount': rec.product_uom_qty,
                        'product_id': rec.product_id.id,
                        'product_uom_id': rec.product_uom.id,
                        'stock_picking_line_id': rec.id,
                    }
                    self.env['account.analytic.line'].sudo().create(create_account_analytic)
                # Crea apunte analítico de contrapartida
                if self.code != 'incoming':
                    for rec in self.move_ids_without_package:
                        create_account_analytic2 = {
                            'name': rec.description_picking,
                            'account_id': rec.location_id.account_analytic_id.id,
                            'partner_id': self.partner_id.id,
                            'date': fields.datetime.now(),
                            'company_id': self.env.company.id,
                            'amount': -(rec.standard_price_t * a) / monetary.rate,
                            'unit_amount': rec.product_uom_qty,
                            'product_id': rec.product_id.id,
                            'product_uom_id': rec.product_uom.id,
                            'stock_picking_line_id': rec.id,
                        }
                        self.env['account.analytic.line'].sudo().create(create_account_analytic2)
        else:
            return True


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

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location'].search([('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id), ('location_id.usage', '!=', 'supplier')]).ids
                if self.env['stock.move'].search([
                        ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                        ('product_qty', '>', 0),
                        ('location_id', 'in', wh_location_ids),
                        ('move_orig_ids', '=', False),
                        ('picking_id', 'not in', self.ids),
                        ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        # enlaza placa con numero de serie
        for rec in self.move_line_ids_without_package:
            rec.lot_id.compute_plaque_id()
        # Crea registro de cuenta analiticas
        self.compute_account_analytic_cost()
        return True








