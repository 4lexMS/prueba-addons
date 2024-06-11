from odoo import _, api, fields, models
from odoo import tools
from odoo.exceptions import ValidationError

class ResConexion(models.Model):
    _name = 'res.conexion'
    _description = 'Integralis Conexion'

    name = fields.Char()
    state = fields.Selection(
        string="Estado",
        selection=[('disabled', "Deshabilitado"), ('production', "Producción"), ('test', "Modo de prueba")],
        default='disabled', copy=False)
    compute_state = fields.Char(compute='compute_control_state')
    provider = fields.Selection(selection=[('none', "No hay proveedor establecido")], default='none')
    user_test = fields.Char('Usuario test')
    user_prod = fields.Char('Usuario producción')
    password_test = fields.Char('Contraseña test')
    password_prod = fields.Char('Contraseña producción')
    token_test = fields.Char()
    token_prod = fields.Char('Token producción')
    api_test = fields.Char('Api/URL test')
    api_prod = fields.Char('Api/URL producción')
    port_test = fields.Char('Puerto test')
    port_prod = fields.Char('Puerto producción')
    root_path_test = fields.Char()
    root_path_prod = fields.Char('Root path producción')
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)

    @api.constrains('state')
    def constrains_state(self):
        for conexion_id in self:
            conexion_id.set_res_conexion()

    def get_environment(self):
        environment = "test"
        if tools.config.get('server_env', False) and tools.config['server_env'] == "PROD":
            environment = "production"
        return environment

    @api.depends('state')
    def compute_control_state(self):
        for conexion_id in self:
            conexion_id.set_res_conexion()
            conexion_id.compute_state = conexion_id.state

    def set_res_conexion(self):
        if self.state != 'disabled':
            environment = self.get_environment()
            if environment not in ['production', self.state]:
                self.state = environment

    @api.model
    def get_api_connection(self, provider):
        """Obtener la conexión para el provider indicado
        :param provider: Provider para la busqueda de conexiones
        :returns record res.conexion: Conexion del provider"""
        res_conexion_id = self.search([('provider', '=', provider), ('state', '!=', 'disabled')], limit=1)
        return res_conexion_id

    @api.model
    def get_fields_required(self):
        """Lista de campos requeridos para la conexión
        dependiendo del provider heredar el método
        :param vals(dict): Datos de la conexión
        :returns list: Lista de campos requeridos"""
        return []

    def check_required_fields(self):
        """Verificar que los campos requeridos esten completos
        :ValidationError: Excepcion si hay campos vacios
        :returns Boolean: True si los campos requeridos estan llenos"""
        fields = self.get_fields_required()
        empty_fields = [self._fields[field].string for field in fields if not self[field]]
        if empty_fields:
            raise ValidationError(_('Por favor completar todos los campos en la conexión:\n %s', "\n".join(empty_fields)))
        return True

    def get_api_url(self):
        """Obtener el Url de la API, dependiendo del estado produccion o test
        :returns str: Url completa incluido el puerto
        """
        url = ""
        if self.state == "production":
            url = "%s:%s" % (self.api_prod, self.port_prod)
        elif self.state == "test":
            url = "%s:%s" % (self.api_test, self.port_test)
        return url

    def get_api_user(self):
        """Obtener el usuario, dependiendo del estado produccion o test
        :returns str: Usuario tomado segun estado, caso contrario vacio
        """
        if self.state =="disabled":
            return ""
        return self.user_prod if self.state == "production" else self.user_test

    def get_api_password(self):
        """Obtener la contraseña, dependiendo del estado  produccion o test
        :returns str: Contraseña tomada segun estado, caso contrario vacio
        """
        if self.state =="disabled":
            return ""
        return self.password_prod if self.state == "production" else self.password_test

