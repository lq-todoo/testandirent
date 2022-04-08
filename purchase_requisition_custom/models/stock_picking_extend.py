from odoo import fields, models, api


class stock_picking_extend(models.Model):
    _inherit = 'stock.picking'

    requisition_id = fields.Many2one(comodel_name='purchase.requisition', string='Acuerdos de compra')
    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')],
                            'Operación', related='picking_type_id.code')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='A almacén', related='location_dest_id.warehouse_id')
    activity_id = fields.Integer(string='id actividad', store=True)     # id de la actividad asignada

    # Actualización de la función del boton como por hacer
    def action_confirm(self):
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

