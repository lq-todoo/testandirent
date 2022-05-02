# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError

class purchase_requisition_extend(models.Model):
    _inherit = 'purchase.requisition'

    department_id = fields.Many2one(comodel_name='hr.department', related='user_id.department_id',
                                   string='Departamento', store=True)

    manager_id = fields.Many2one(comodel_name='hr.employee', related='user_id.department_id.manager_id', string='Jefe del área',
                             help='Jefe inmediato respondable de su aprobación')
    manager2_id = fields.Many2one(comodel_name='hr.employee', related='manager_id.parent_id', string='Aprobación alternativa',
                             help='Cuando el jefe inmediato se encuentra ausente, debe aprobar el siguiente respondable')
    available = fields.Boolean(string='habilitado', compute='_domain_ochange_x_partner')
    activity_id = fields.Integer(string='id actividad')
    # Obtiene la fecha y hora actual
    current_date = fields.Datetime('Fecha actual', required=False, readonly=False, select=True,
                                   default=lambda self: fields.datetime.now())
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    purchase_ids2 = fields.One2many(comodel_name='stock.picking', inverse_name='requisition_id',
                                    string='Stock picking',
                                    states={'done': [('readonly', True)]})
    stock_picking_count = fields.Integer(compute='_compute_stock_picking_number', string='Numero de transferencias')
    show_picking = fields.Boolean(string='Picking', store=True,
                                  help='Mostrar/ocultar el campo cantidad de producto en stock')

    ticket_many2many = fields.Many2many(comodel_name='helpdesk.ticket', relation='x_helpdesk_ticket_purchase_requisition_rel',
                                  column1='purchase_requisition_id', column2='helpdesk_ticket_id', string='Tickets')
    tickets_count = fields.Integer(compute='_compute_tickets_number', string='Numero de transferencias')
    c = fields.Integer(string='c', store=False)
    cc = fields.Integer(string='cc', store=False)
    len_id = fields.Integer(string='longitud', store=False)
    x_stock_picking_transit = fields.One2many(comodel_name='stock_picking_transit', inverse_name='requisition_id',
                                  string='Stock picking transitorio')

    # Función boton refrescar
    def action_show_picking(self):
        for rec in self.line_ids:
            rec.compute_qty_available_location()

    # Acción de button tranferencia inmediata
    def action_stock_picking_create(self):
        # Contador de tranferencias
        comprob = self.env['stock.picking'].search([('requisition_id', "=", self.id), ('stage', '=', [1, 2])])
        a = len(comprob.ids)
        if a == 0:
            self.write({'x_stock_picking_transit': [(5)]})  # Limpiar/deslinkear registros del modelo
            self.update_purchase_requisition_line()  # Función que actualiza las cantidades disponibles en productos repetidos
            self._stock_picking_create()    # Función que genera las tranferencias dependiedo las ubicaciones a mover
            self.association_stock_picking()    # Función asociar stock pickink padre
            self.stock_picking_transit_unlink()   # Función que deslinkea todas las lienas stock picking transit
        elif a > 0:
            raise UserError('Existen tranferencias inmediatas asociadas,si desea realizar una nueva transferencia debe eliminar las existentes')
        return True

    # Actualización de estado de stock picking de la  etapa 1
    def update_stock_picking_stage(self):
        stage1 = self.env['stock.picking'].search([('stage', '=', 1), ('requisition_id', '=', self.ids)])
        stage_move1 = self.env['stock.move'].search([('stage', '=', 1)])
        for stage2 in stage1:
            stage2.write({'state': 'assigned'})
        for stage_move2 in stage_move1:
            stage_move2.write({'state': 'assigned'})

    # Función que actualiza las cantidades disponibles en productos repetidos
    def update_purchase_requisition_line(self):
        # obj
        lis = []
        loct = []
        price = []
        loct_uniq = []
        list_uniq = []
        price_uniq = []
        count = 0
        c = 0
        t = 0
        l = 0
        for rec in self.line_ids:
            #a = [rec.id, rec.product_id.id, rec.qty_location, rec.location.id, rec.inventory_product_qty]
            #b.append(b)     # ids y valores de line_ids
            for rec2 in self.line_ids:
                if rec != rec2 and rec.product_id == rec2.product_id:
                    count += 1
                    loct.append(rec.location.id)
                    lis.append(rec.product_id.id)
                    if count < 2:
                        t = rec.qty_location # Se guarada cantidad inicial
        loct_uniq = list(set(loct))  # id de location repetido
        list_uniq = list(set(lis))  # id de producto repetido
        if len(list_uniq) == 1 and len(loct_uniq) == 1:
            for rec3 in self.line_ids:
                # compuebo que son las lineas correspondientes
                if rec3.product_id.ids == list_uniq and rec3.location.ids == loct_uniq:
                    # Calculo de cantidad de productos a mover por ubicacación
                    if l < 1:  # para no sacra más de lo pedido
                        c = t
                        t = t - rec3.product_qty2
                        if t > 0:  # mientras la cantidad de la ubicación sea mayor q la pedida
                            now_quantity = abs(c)
                        elif t < 0:
                            l += 1
                            now_quantity = abs(c)
                        elif t == 0:
                            now_quantity = 0
                    # Actualización de cantidades disponibles para productos repetidos
                    self.write({'line_ids': [(1, rec3.id, {'qty_location': now_quantity})]})

    # Función que deslinkea todas las lienas stock picking transit
    def stock_picking_transit_unlink(self):
        self.write({'x_stock_picking_transit': [(5)]})

    # Función que genera las tranferencias dependiedo las ubicaciones a mover
    def _stock_picking_create(self):
        if self.line_ids:
            # variables
            # ------------------------------------------- PASO 1 ------------------------------------------
            transit_list = []    # vector ubicaciones origen
            tansit_stock = []
            long = 0   # cantidad de productos diferentes asignados
            # Calculos para optner las ubicaciones de transición
            for l1 in self.line_ids:
                if l1.inventory_product_qty > 0:    # comprueba que exista cantidades en la requisición
                    long += 1   # comprueba si etiste una cantidad asignada para cantidad en inventario
                    # Se optiene las ubicaciones internas filtrado por locación/ubicación interna/!=0/producto
                    line_ids_stock_picking = self.env['stock.quant'].search(
                        [('location_id.usage', '=', 'internal'), ('product_id', '=', l1.product_id.id),
                         ('location', '=', l1.location.id), ('available_quantity', '!=', 0)], order='available_quantity DESC')
                    h = 0  # sumatoria disponibilidad producto x ubicación
                    p = 0  # valor para condición cantidades x ubicación
                    for locat in line_ids_stock_picking:  # Recorre las ubicaciones internas en inventario del producto
                        # Optiene vector de ubicaciones origen de forma ordenada
                        transit_list.append(locat.location_id.transit_location_id.id)  # lista de ubicaciones de transito
                        transit_stock = list(set(transit_list))  # lista de ubicaciones de transito para crear stock picking

            # generación stock pickin de ubicación de origen a ubicación transición
            if long > 0: # comprueba si etiste una cantidad asignada para cantidad en inventario
                for l2 in transit_stock:
                    transit_stock_picking = self.env['stock.location'].search([('id', '=', l2)], limit=1)
                    create_vals = {'stage': 1,
                                   #'state': 'assigned',
                                   'origin': self.name,
                                   'scheduled_date': self.date_end,
                                   'location_id': transit_stock_picking.warehouse_id.lot_stock_id.id,
                                   'picking_type_id': transit_stock_picking.warehouse_id.int_type_id.id,
                                   'location_dest_id': transit_stock_picking.transit_location_id.id,
                                   }
                    stock_picking_id = self.env['stock.picking'].sudo().create(create_vals)
                    #self.write({'line_ids': [(1, stock_picking_id.id, {'state': 'assigned'})]})
                    # Código que crea una nueva actividad
                    if transit_stock_picking.warehouse_id.employee_id:
                        create_activity = {
                            'activity_type_id': 4,
                            'summary': 'Transferencia, ubicación de origen a transito:',
                            'automated': True,
                            'note': 'A sido asignado para validar la transferencia inmediata',
                            'date_deadline': fields.datetime.now(),
                            'res_model_id': self.env['ir.model']._get_id('stock.picking'),
                            'res_id': stock_picking_id.id,
                            'user_id': transit_stock_picking.warehouse_id.employee_id.user_id.id,
                            }
                        new_activity = self.env['mail.activity'].sudo().create(create_activity)
                        # Escribe el id de la actividad en un campo
                        stock_picking_id.write({'activity_id': new_activity.id})
                    else:
                        raise UserError('Se debe selecionar un encargado de almacen para poder asignar una tarea.')

            dest_list = []
            dest_stock = []
            dest_quantity = 0
            # Calculos y escritura al modelo para generar los stock pinking de ubicación de origen a transito
            if long > 0:    # comprueba si etiste una cantidad asignada para cantidad en inventario
                for rec1 in self.line_ids:
                    t = rec1.inventory_product_qty
                    c = 0
                    l = 0
                    # Optiene el producto disponible en distintas ubicaciones internas y ordena de mayor a menor
                    stock_quant = self.env['stock.quant'].search(
                        [('location_id.usage', '=', 'internal'), ('product_id', '=', rec1.product_id.id),
                        ('location', '=', rec1.location.id), ('available_quantity', '!=', 0)], order='available_quantity DESC')
                    for rec2 in stock_quant:
                        # Calculo de cantidad de productos a mover por ubicacación
                        if l < 1:   # para no sacra más de lo pedido
                            c = t
                            t = rec2.available_quantity - t
                            if t > 0:   # mientras la cantidad de la ubicación sea mayor q la pedida
                                l += 1
                                dest_quantity = abs(c)
                            elif t < 0: # mientras la cantidad de la ubicación sea menor q la pedida
                                dest_quantity = rec2.available_quantity
                            elif t == 0:    # mientras la cantidad de la ubicación sea igual q la pedida
                                dest_quantity = rec2.available_quantity
                        else:
                            dest_quantity = 0
                        # Rastreo de stock picking
                        ontner_stock_picking = self.env['stock.picking'].search([('requisition_id', '=', rec1.requisition_id.ids), ('location_dest_id', '=', rec2.location_id.transit_location_id.ids)], limit=1)
                        # Creación de registros necearios para el stock picking move
                        self.write({'x_stock_picking_transit': [(0, 0, {'stage': 1,
                                                                        'stock_picking_id': ontner_stock_picking.id,
                                                                        'product_id': rec1.product_id.id,
                                                                        'product_description_variants': rec1.product_description_variants,
                                                                        'picking_type_id': rec2.location_id.warehouse_id.in_type_id.id,
                                                                        'origin_location': rec1.location.id,
                                                                        'origin_warehouse_id': rec2.location_id.warehouse_id.id,
                                                                        'origin_location_id': rec2.location_id.id,
                                                                        'parent_location_id': rec2.location_id.warehouse_id.lot_stock_id.id,
                                                                        'transit_location_id': rec2.location_id.transit_location_id.id,
                                                                        'dest_warehouse_id': rec1.warehouse_id.id,
                                                                        'dest_location_id': rec1.default_location_dest_id.id,
                                                                        'concatenate_location': str(rec2.location_id.transit_location_id.id) + ', ' + str(rec1.default_location_dest_id.id),
                                                                        'account_analytic_id': rec1.account_analytic_id.id,
                                                                        'available_quantity_total': rec1.available_quantity_total,
                                                                        'qty_location': rec2.available_quantity,
                                                                        'quantity': dest_quantity,
                                                                        'observations': rec1.observations,
                                                                        })]})
                        #  concatenas ubicación de transición con ubicación de destino, para poder compara
                        name = str(rec2.location_id.transit_location_id.id) + ', ' + str(rec1.default_location_dest_id.id),
                        dest_list.append(name)
                        dest_stock = list(set(dest_list))

            # Cración de registros linea de productos de tranferecia inmediata
            if long > 0:    # comprueba si etiste una cantidad asignada para cantidad en inventario
                for l3 in self.x_stock_picking_transit:
                    if l3.stage == 1 and l3.quantity != 0:
                        create_vals2 = {
                            'stage': 1,
                            #'state': 'assigned',
                            'origin': self.name,
                            'name': l3.name_picking,
                            'picking_id': l3.stock_picking_id.id,
                            'product_id': l3.product_id.id,
                            'product_uom': 1,
                            'product_uom_qty': l3.quantity,
                            'quantity_done': 0,
                            'description_picking': l3.name_picking,
                            'location_id': l3.origin_location_id.id,
                            'location_dest_id': l3.transit_location_id.id,
                            'date_deadline': self.date_end,
                        }
                        self.env['stock.move'].sudo().create(create_vals2)

            # ------------------------------------------- PASO 2 ------------------------------------------
            c = 0
            # generación stock pickin de ubicación de origen a ubicación transición
            if long > 0:    # comprueba si etiste una cantidad asignada para cantidad en inventario
                for rec3 in dest_stock:
                    c = c + 1
                    dest_stock_picking = self.env['stock_picking_transit'].search([('concatenate_location', '=', rec3)], limit=1)
                    create_vals = {'stage': 2,
                                   'origin': dest_stock_picking.stock_picking_id.name,
                                   'scheduled_date': self.date_end,
                                   'location_id': dest_stock_picking.transit_location_id.id,
                                   'picking_type_id': dest_stock_picking.dest_warehouse_id.int_type_id.id,
                                   'location_dest_id': dest_stock_picking.dest_location_id.id,
                                   }
                    stock_picking_id = self.env['stock.picking'].sudo().create(create_vals)
                    # Código que crea una nueva actividad
                    if transit_stock_picking.warehouse_id.employee_id:
                        create_activity = {
                            'activity_type_id': 4,
                            'summary': 'Transferencia, ubicación de transito a destino:',
                            'automated': True,
                            'note': 'A sido asignado para validar la transferencia inmediata',
                            'date_deadline': fields.datetime.now(),
                            'res_model_id': self.env['ir.model']._get_id('stock.picking'),
                            'res_id': stock_picking_id.id,
                            'user_id': transit_stock_picking.warehouse_id.employee_id.user_id.id,
                        }
                        new_activity = self.env['mail.activity'].sudo().create(create_activity)
                        # Escribe el id de la actividad en un campo
                        stock_picking_id.write({'activity_id': new_activity.id})
                    else:
                        raise UserError('Se debe selecionar un encargado de almacen para poder asignar una tarea.')

            # Calculos y escritura al modelo para generar los stock pinking line de ubicación de transito a destino
            if long > 0:    # comprueba si etiste una cantidad asignada para cantidad en inventario
                for rec4 in self.line_ids:
                    t = rec4.inventory_product_qty
                    c = 0
                    l = 0
                    # Optiene el producto disponible en distintas ubicaciones internas y ordena de mayor a menor
                    stock_quant2 = self.env['stock.quant'].search(
                        [('location_id.usage', '=', 'internal'), ('product_id', '=', rec4.product_id.id),
                         ('location', '=', rec4.location.id), ('available_quantity', '!=', 0)], order='available_quantity DESC')
                    for rec5 in stock_quant2:
                        # Calculo de cantidad de productos a mover por ubicacación
                        if l < 1:
                            c = t
                            t = rec5.available_quantity - t
                            if t > 0:
                                l += 1
                                dest_quantity = abs(c)
                            elif t < 0:
                                dest_quantity = rec5.available_quantity
                            elif t == 0:
                                dest_quantity = rec5.available_quantity
                        else:
                            dest_quantity = 0
                        # Rastreo de stock picking
                        ontner_stock_picking2 = self.env['stock.picking'].search(
                            [('requisition_id', '=', rec4.requisition_id.ids),
                             ('location_id', '=', rec5.location_id.transit_location_id.id),
                             ('location_dest_id', '=', rec4.default_location_dest_id.ids)], limit=1)
                        # Creación de registros necesarios para el stock picking move
                        self.write({'x_stock_picking_transit': [(0, 0, {'stage': 2,
                                                                        'stock_picking_id': ontner_stock_picking2.id,
                                                                        'product_id': rec4.product_id.id,
                                                                        'product_description_variants': rec4.product_description_variants,
                                                                        'picking_type_id': rec4.picking_type_id.id,
                                                                        'origin_location': rec4.location.id,
                                                                        'origin_warehouse_id': rec5.location_id.transit_location_id.warehouse_id.id,
                                                                        'origin_location_id': rec5.location_id.transit_location_id.id,
                                                                        'parent_location_id': rec5.location_id.warehouse_id.lot_stock_id.id,
                                                                        'dest_warehouse_id': rec4.warehouse_id.id,
                                                                        'dest_location_id': rec4.default_location_dest_id.id,
                                                                        'concatenate_location': str(rec5.location_id.transit_location_id.id) + ', ' + str(rec4.default_location_dest_id.id),
                                                                        'account_analytic_id': rec4.account_analytic_id.id,
                                                                        'available_quantity_total': rec4.available_quantity_total,
                                                                        'qty_location': rec5.available_quantity,
                                                                        'quantity': dest_quantity,
                                                                        'observations': rec4.observations,
                                                                        })]})
            # Cración de registros linea de productos de tranferecia inmediata
            if long > 0:    # comprueba si etiste una cantidad asignada para cantidad en inventario
                for rec6 in self.x_stock_picking_transit:
                    if rec6.stage == 2 and rec6.quantity != 0:
                        create_vals2 = {'stage': 2,
                                        'origin': rec6.stock_picking_id.name,
                                        'name': rec6.name_picking,
                                        'picking_id': rec6.stock_picking_id.id,
                                        'product_id': rec6.product_id.id,
                                        'product_uom': 1,
                                        'product_uom_qty': rec6.quantity,
                                        'quantity_done': 0,
                                        'description_picking': rec6.name_picking,
                                        'location_id': rec6.origin_location_id.id,
                                        'location_dest_id': rec6.dest_location_id.id,
                                        'date_deadline': self.date_end,
                                        }
                        self.env['stock.move'].sudo().create(create_vals2)

    # Función asociar stock pickink padre
    def association_stock_picking(self):
        association1 = self.env['stock_picking_transit'].search(
            [('requisition_id', '=', self.ids), ('stage', '=', 1)])
        association2 = self.env['stock_picking_transit'].search(
            [('requisition_id', '=', self.ids), ('stage', '=', 2)])
        for rec1 in association1:
            for rec2 in association2:
                if rec1.product_id == rec2.product_id and rec1.transit_location_id == rec2.origin_location_id and rec1.dest_location_id == rec2.dest_location_id:
                    stock_picking_id = self.env['stock.picking'].search(
                        [('requisition_id', '=', self.ids), ('stage', '=', 2),
                         ('location_id', '=', rec2.origin_location_id.id),
                         ('location_dest_id', '=', rec2.dest_location_id.id)], limit=1)
                    stock_picking_id.write({'parent_stock_picking': rec1.stock_picking_id.id})

    # Cuenta las trasnferencias inmediatas asociadas a la acuerdo de compra
    @api.depends('purchase_ids2')
    def _compute_stock_picking_number(self):
        for requisition in self:
            requisition.stock_picking_count = len(requisition.purchase_ids2)

    # Cuenta los tickets asociadoss a los acuerdos de compra
    @api.depends('ticket_many2many')
    def _compute_tickets_number(self):
        for tickets in self:
            tickets.tickets_count = len(tickets.ticket_many2many)

    # Indica si el jefe inmediato está o no está ausente
    @api.depends('time_off_related')
    def _compute_number_of_days(self):
        if self.time_off_related == False:
            self.time_off = 'Disponible'
        else:
           self.time_off = 'Ausente'
           self.write({'manager2_id': self.manager_id.parent_id})
        return self.time_off

    # Sirve para indicar si está habilitado para aprobar solicitudes de compra
    @api.model
    def _domain_ochange_x_partner(self):
        if self.state == 'ongoing' or self.state == 'open':
            self.write({'available': True})
        else:
            self.write({'available': False})

    # función botón cancelar
    def action_cancel(self):
        # try to set all associated quotations to cancel state
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
            requisition.purchase_ids.button_cancel()
            for po in requisition.purchase_ids:
                po.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
        self.write({'state': 'cancel'})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es rechazado')

    # función botón cancelar extendida
    def action_cancel_extend(self):
        if self.manager_id.user_id == self.env.user or (self.manager2_id.user_id == self.env.user and self.time_off_related == True):
            #  Marca actividad como hecha de forma automatica
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es rechazado')
            # try to set all associated quotations to cancel state
            for requisition in self:
                for requisition_line in requisition.line_ids:
                    requisition_line.supplier_info_ids.unlink()
                requisition.purchase_ids.button_cancel()
                for po in requisition.purchase_ids:
                    po.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
            self.write({'state': 'cancel'})
        else:
            raise UserError('No cuenta con el permiso para rechazar acuerdos de compra, por favor comunicarse con su jefe inmediato para aprobar este acuerdo de compra.')

    # función del boton validar
    def action_in_progress_extend(self):
        if self.manager_id or self.user_id.employee_id.general_manager == True:
            self.update_purchase_requisition_line()  # Función que actualiza las cantidades disponibles en productos repetidos
            self._verification_requisition_line()       # Función de verificación de lineas de requisición
            self.ensure_one()
            if not self.line_ids:
                raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))
            if self.type_id.quantity_copy == 'none' and self.vendor_id:
                for requisition_line in self.line_ids:
                    if requisition_line.price_unit <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without price.'))
                    if requisition_line.product_qty <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without quantity.'))
                    requisition_line.create_supplier_info()
                self.write({'state': 'ongoing'})
            #     Crear actividad al jefe inmediato si esta disponible
            elif self.manager_id and self.time_off_related == False:
                self.write({'state': 'in_progress'})
                # suscribe el contacto que es gerente del representante del proveedor en acuerdos de compra
                self.message_subscribe(self.manager_id.user_id.partner_id.ids)
                # Código que crea una nueva actividad
                model_id = self.env['ir.model']._get(self._name).id
                create_vals = {
                    'activity_type_id': 4,
                    'summary': 'Acuerdo de compra:',
                    'automated': True,
                    'note': 'A sido asignado para aprobar el siguiente acuerdo de compra',
                    'date_deadline': self.current_date.date(),
                    'res_model_id': model_id,
                    'res_id': self.id,
                    'user_id': self.manager_id.user_id.id
                }
                new_activity = self.env['mail.activity'].create(create_vals)
                # Escribe el id de la actividad en un campo
                self.write({'activity_id': new_activity})
            #     Crear actividad al jefe del jefe inmediato si esta ausente
            elif self.manager_id and self.time_off_related == True:
                self.write({'state': 'in_progress'})
                # suscribe el contacto que es gerente del representante del proveedor en acuerdos de compra
                self.message_subscribe(self.manager2_id.user_id.partner_id.ids)
                # Código que crea una nueva actividad
                model_id = self.env['ir.model']._get(self._name).id
                create_vals = {
                    'activity_type_id': 4,
                    'summary': 'Acuerdo de compra:',
                    'automated': True,
                    'note': 'A sido asignado para aprobar el siguiente acuerdo de compra, el jefe responsable se encuentra ausente',
                    'date_deadline': self.current_date.date(),
                    'res_model_id': model_id,
                    'res_id': self.id,
                    'user_id': self.manager2_id.user_id.id
                }
                new_activity = self.env['mail.activity'].create(create_vals)
                # Escribe el id de la actividad en un campo
                self.write({'activity_id': new_activity})
            # Set the sequence number regarding the requisition type / Agrega la secuencia de acuerdo de compra
            if self.name == 'New':
                if self.is_quantity_copy != 'none':
                    self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
                else:
                    self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')
        else:
            raise UserError('El departamento no tiene un gerente asociado, o usted no tiene asociado un departamento, por favor cumunicase con su administrador')

    # Función del boton aprobación, y tambien puede aprobar el jefe inmediato si no se encuentra el responsable de aprobación
    def action_approve(self):
        self._verification_requisition_line()       # Función de verificación de lineas de requisición
        self.update_purchase_requisition_line()  # Función que actualiza las cantidades disponibles en productos repetidos
        if (self.manager_id.user_id == self.env.user and self.manager_id.active_budget == True) or (self.manager2_id.user_id == self.env.user and self.time_off_related == True):
            # Cambio de etapa
            self.write({'state': 'open'})
            #  Marca actividad como hecha de forma automatica
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es aprobado')
        elif self.manager_id.user_id == self.env.user and self.manager_id.active_budget == False:
            raise UserError(
                'No tiene asignado un monto de presupuesto o activa la opcíón sin tope, por favor comunicarse con el administrador para realizar asignación')
        else:
            raise UserError('No cuenta con el permiso para aprobar acuerdos de compra, por favor comunicarse con su jefe inmediato para aprobar este acuerdo de compra.')

    # Función de verificación de lineas de requisición
    def _verification_requisition_line(self):
        for rec in self.line_ids:
            if rec.product_qty2 == 0:
                raise UserError('Existen lienas que no tienen una cantidad asignada')
            if rec.default_location_dest_id == False:
                raise UserError('Existen lienas que no tienen almacen/ubicación de destino')
            if rec.warehouse_id:
                return
            else:
                raise UserError('Existen lienas que no tienen almacen/ubicación de destino')

    # función que llama función confirmar en stock picking
    def call_action_confirm(self):
        for rec in self.purchase_ids2:
            if rec.stage == 1:
                rec.action_confirm()

























