{
    'name': 'Integralis integration with SAP',
    'version': '17.0.0.1.0',
    'summary': 'Integracion con SAP',
    'description': """
    * Integracion con SAP para gestion del Website
    """,
    'author': "zabyca",
    'contributors': ['Fabii-Auz',],
    'author': 'Zabyca',
    'website': 'http://www.zabyca.com',
    'license': 'OPL-1',
    'category': 'Integralis',
    'depends': ['website','integralis_conexion'],
    'data': [
        'data/cron_data.xml',
        'security/ir.model.access.csv',
        'views/res_conexion_view.xml',
        'views/sap_connector_view.xml',],
    'assets': {},
    'auto_install': False,
    'application': False,

}
