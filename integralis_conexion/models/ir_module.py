from odoo import _, api, fields, models


class IrModule(models.Model):
    _inherit = "ir.module.module"

    def _get_modules_to_load_domain(self):
        conexion_ids = self.env['res.conexion'].search([('state', '!=', 'disabled')])
        conexion_ids.constrains_state()
        return super()._get_modules_to_load_domain()
