import logging
from odoo import api,fields, models, tools
from ..connection.sap_connection import SAP

_logger = logging.getLogger(__name__)

class SapSession(models.Model):
    _name = 'sap.session'

    name = fields.Char()
    res_conexion_id =  fields.Many2one(
        comodel_name='res.conexion',
        check_company=True,
        required=True,
        domain=[['provider', '=', "sap"]],
    )
    sap_session_id = fields.Char("Session ID")
    sap_route_id = fields.Char("Route ID")
    state = fields.Selection(
        string="Estado",
        selection=[('draft', "Borrador"), ("logged", "Session Iniciada"), ("closed", "Session Cerrada")],
        default='draft', copy=False, readonly=True)

    @api.model
    def cron_download_products_from_sap(self):
        """Download products from API SAP"""
        #TODO Crear la vista para completar la información y ubicar el boton de inicio de sesion
        session_id = self.create({"res_conexion_id": self.res_conexion_id.get_api_connection("sap").id, "name": "Sesion SAP Pruebas"})
        session_id.action_sap_login()
        session_id.action_sap_download_products()
        session_id.action_sap_logout()
        return True

    def action_sap_login(self):
        """Iniciar sesión en SAP"""
        self.ensure_one()
        conection = self.res_conexion_id
        if conection and conection.state != "disabled" and conection.check_required_fields():
            sap = self.get_new_instance_sap()
            data = {"CompanyDB": conection._get_sap_db(), "Password": conection.get_api_password(),"UserName": conection.get_api_user() }
            response = sap.post("/Login", data)
            rsp_json = response.json()
            if rsp_json.get("error", ""):
                _logger.error(
                "Error en login SAP. Detalle del error: %s" %
                rsp_json["error"].get("message",{}).get("value")
            )
            elif rsp_json.get("SessionId", ""):
                self.write({
                    "sap_session_id": rsp_json["SessionId"],
                    "sap_route_id": response.cookies.get('ROUTEID', ""),
                    "state": "logged"
                })

    def action_sap_logout(self):
        """Cerrar sesión en SAP"""
        self.ensure_one()
        sap = self.get_new_instance_sap()
        response = sap.post("/Logout")
        self.write({
            "sap_session_id": "",
            "sap_route_id": "",
            "state": "closed"
        })


    def action_sap_download_products(self):
        """Descargar productos desde SAP"""
        self.ensure_one()
        sap = self.get_new_instance_sap()
        params = {"$filter": "startswith(U_HV_Subir_Web, 'SI')",
                  "$orderby": "ItemCode"}
        # Llamar al endpoint para conocer el total de los items
        # y obtener todos los productos para paginacion se usa skip
        response_count = sap.get("/Items/$count", params=params)
        total_items = response_count.json()
        if isinstance(total_items, dict) and total_items.get("error", ""):
                _logger.error(
                "Error al descargar productos de SAP. Detalle del error: %s" %
                total_items["error"].get("message",{}).get("value")
                )
                return
        count = 0
        skip = 0
        has_items = True
        while has_items:
            response = sap.get("/Items", params=params)
            items = response.json()
            if items.get("error", ""):
                _logger.error(
                "Error al descargar productos de SAP. Detalle del error: %s" %
                items["error"].get("message",{}).get("value")
                )
                return
            pag_items = len(items.get("value", []))
            if total_items > pag_items:
                skip += pag_items
                params["$skip"] = skip
            else:
                has_items = False
            for item in items.get("value", []):
                count += 1
                _logger.info("Descargando Producto %s de %s", count, total_items)
                self._find_create_product(item)

    @api.model
    def _find_create_product(self, item_vals):
        ProductModel = self.env["product.product"]
        product_vals = self._prepare_product_vals(item_vals)
        product = ProductModel.search([("default_code", "=", product_vals["default_code"])], limit=1)
        try:
            with self.env.cr.savepoint():
                if product:
                    _logger.info("Actualizando Producto con codigo: %s", product.default_code)
                    product.write(product_vals)
                else:
                    _logger.info("Creando Producto con codigo: %s", product_vals["default_code"])
                    product = ProductModel.create(product_vals)
        except Exception as e:
             _logger.error("Error al guardar productos, Detalle del error: %s" % tools.ustr(e))
        return product

    @api.model
    def _prepare_product_vals(self, item_vals):
        values = {
            "default_code": item_vals.get("ItemCode") or "",
            "name": item_vals.get("ItemName") or "",
            "is_published": True
        }
        return values

    def get_new_instance_sap(self):
        return SAP(
            api_url = self.res_conexion_id.get_api_url(),
            session_id=self.sap_session_id or None,
            route_id=self.sap_route_id or None)