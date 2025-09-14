from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_api_token = fields.Char(
        string='Twilio API Token',
        config_parameter='whatsapp.api_token',
        help='Twilio credentials in format: ACCOUNT_SID|AUTH_TOKEN'
    )
    
    whatsapp_employee_phone = fields.Char(
        string='Employee Phone Number',
        config_parameter='whatsapp.employee_phone',
        help='Phone number of the employee to notify for new orders (with country code, e.g., +1234567890)'
    )
    
    whatsapp_from_number = fields.Char(
        string='WhatsApp From Number',
        config_parameter='whatsapp.from_number',
        help='Your Twilio WhatsApp-enabled phone number (e.g., +14155551234). Leave empty to use sandbox number for testing.'
    )
    
    whatsapp_customer_template_sid = fields.Char(
        string='Customer Template SID',
        config_parameter='whatsapp.customer_template_sid',
        default='HX8264756fadd035142c0905cca6b6b594',
        help='Twilio WhatsApp template SID for customer order confirmations'
    )
    
    whatsapp_employee_template_sid = fields.Char(
        string='Employee Template SID',
        config_parameter='whatsapp.employee_template_sid',
        default='HX3e140b59baa66fb67a2172a7442ec2d1',
        help='Twilio WhatsApp template SID for employee notifications'
    )
    
