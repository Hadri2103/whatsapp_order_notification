{
    'name': 'WhatsApp Order Notification',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Send WhatsApp notifications to customers after order confirmation',
    'description': """
        This module sends WhatsApp messages to customers when they place an order
        on the ecommerce website, regardless of payment status.
        
        Uses Twilio WhatsApp Business API with approved message templates.
    """,
    'author': 'Hadrien Plancq',
    'website': 'https://www.orca-consult.be',
    'depends': ['sale', 'website_sale'],
    'external_dependencies': {
        'python': ['twilio'],
    },
    'data': [
        'data/whatsapp_template.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}