import logging
from odoo import api,fields, models

_logger = logging.getLogger(__name__)

class ResConexion(models.Model):
    _inherit = 'res.conexion'

    provider = fields.Selection(selection_add=[
            ('sap', 'SAP'),
        ])
    sap_db_test = fields.Char("BD SAP Test")
    sap_db_prod = fields.Char("BD SAP Producción")

    def get_fields_required(self):
        if self.provider != "sap":
            return super().get_fields_required()
        fields = []
        if self.state == "production":
            fields =["api_prod", "port_prod", "user_prod", "password_prod", "sap_db_prod"]
        elif self.state == "test":
            fields =["api_test", "port_test", "user_test", "password_test", "sap_db_test"]
        return fields

    def _get_sap_db(self):
        """Obtener el nombre de la BD, dependiendo del estado  produccion o test
        :returns str: BD tomada segun estado, caso contrario vacio
        """
        if self.state =="disabled":
            return ""
        return self.sap_db_prod if self.state == "production" else self.sap_db_test


