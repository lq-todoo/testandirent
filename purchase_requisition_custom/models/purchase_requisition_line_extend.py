# -*- coding: utf-8 -*-

from odoo import api, fields, models
import json

class purchase_requisition_line_extend(models.Model):
    _inherit = 'purchase.requisition.line'

    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', compute='_compute_product_qty')

    available_quantity_total = fields.Float(string='Stock',
                                 help='Muestra la cantidad disponible que está sin reservar')

    qty_available_location = fields.Float(string='Disponible',
                                 help='Muestra la cantidad disponible en la ubicación selecionada del producto')

    location_id_domain = fields.Char(compute="_compute_location_stock_picking", readonly=True, store=False)
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Tipo de operación')
    property_stock_inventory = fields.Many2one(comodel_name='stock.location',
                                               string='Mover de',
                                               help='Muestra la ubicación del producto en el inventario',
                                               )
    location_dest_id_domain = fields.Char(compute="_compute_location_dest_id", readonly=True, store=False)
    default_location_dest_id = fields.Many2one(comodel_name='stock.location', string='Mover A',
                                               help='Ubicación a mover, con filtro de almacane y ubicación interna, cliente')
    inventory_product_qty = fields.Float(string='Cantidad inventario', compute='_compute_inventory_product_qty',
                                         help='Cantidad de pruductos que deseas sacar o mover de inventario')
    product_qty2 = fields.Float(string='Cantidad', help='Cantidad de pruductos a comprar')

    show_picking = fields.Boolean(string='show', related='requisition_id.show_picking',
                                  help='Mostrar/ocultar el button y smart button de solicitud de compra')

    name_picking = fields.Char(comodel_name='stock.location', related='product_id.name')

    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Almacen', readonly=True,
                                   related='default_location_dest_id.warehouse_id', help='Almacen a mover')

    # Función que aplica filtro dinamico de localización del producto en inventario
    @api.depends('product_id')
    def _compute_location_stock_picking(self):
        for rec in self:
            rec.location_id_domain = json.dumps(
                [('usage', '=', 'internal'), ('id', "=", rec.product_id.stock_quant.location_id.ids)]
            )

    # Función que filtra la ubicación por ubicación tipo cliente e interno, y que tenga un almacen relacionado
    @api.depends('product_id')
    def _compute_location_dest_id(self):
        location_ids = []
        location_id = self.env['stock.location'].search([])
        for r in location_id:
            if r.warehouse_id:
                location_ids.append(r.id)
        for rec in self:
            rec.location_dest_id_domain = json.dumps(
                [('usage', '=', ['internal', 'customer']), ('id', '=', location_ids)]
            )

    #   Función que restablece ubicación y cantidad
    @api.onchange('product_id')
    def _compute_property_stock_inventory(self):
        self.property_stock_inventory = False
        self.qty_available_location = 0

    #   Función que calcula la cantidad de stock por ubicación
    @api.onchange('property_stock_inventory', 'show_picking')
    def _compute_qty_available_location(self):
        c = 0
        for rec in self.product_id.stock_quant:
            if rec.product_id == self.product_id and rec.location_id == self.property_stock_inventory:
                c = c + rec.available_quantity
            self.qty_available_location = c

    #   Función que establece transferencia inmediata por defecto
    @api.onchange('default_location_dest_id')
    def _compute_picking_type_id(self):
        picking_type = self.env['stock.picking.type'].sudo().search([('sequence_code', '=', 'T_INM')], limit=1)
        if self.default_location_dest_id:
            if picking_type.sequence_code == 'T_INM':
                self.picking_type_id = picking_type.id
            else:
                create_stock_picking_type = {
                    'name': 'Default Transferencia Inmediata',
                    'sequence_code': 'T_INM',
                    'code': 'internal',
                    'company_id': self.env.company.id,
                    'warehouse_id': self.property_stock_inventory.warehouse_id.id,
                }
                picking_type2 = self.env['stock.picking.type'].create(create_stock_picking_type)
                self.picking_type_id = picking_type2.id
        else:
            self.picking_type_id = False


    # Función que calcula la cantidad de inventario a mover
    @api.onchange('product_qty2')
    @api.depends('available_quantity_total')
    def _compute_inventory_product_qty(self):
        for rec in self:
            if rec.product_qty2 <= rec.available_quantity_total:
                rec.inventory_product_qty = rec.product_qty2
            else:
                rec.inventory_product_qty = rec.available_quantity_total

    # Función que calcula la cantidad a comprar
    @api.onchange('product_qty2')
    @api.depends('available_quantity_total')
    def _compute_product_qty(self):
        for rec2 in self:
            if rec2.product_qty2 > rec2.available_quantity_total:
                rec2.product_qty = rec2.product_qty2 - rec2.available_quantity_total
            else:
                rec2.product_qty = 0

    # Función que calcula la cantidad disponible en el stock del producto en ubicación interna
    @api.onchange('product_id', 'show_picking')
    # @api.depends('product_id')
    def _compute_available_quantity_total(self):
        c = 0
        if self.product_id.stock_quant:
            for rec in self.product_id.stock_quant:
                if rec.product_id == self.product_id and rec.location_id.usage == 'internal':
                    c = c + rec.available_quantity
                self.available_quantity_total = c
        else:
            self.available_quantity_total = 0



















































