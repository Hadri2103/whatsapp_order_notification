from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_api_url = fields.Char(
        string='WhatsApp API URL',
        config_parameter='whatsapp.api_url',
        help='WhatsApp Business API endpoint URL'
    )
    
    whatsapp_api_token = fields.Char(
        string='WhatsApp API Token',
        config_parameter='whatsapp.api_token',
        help='WhatsApp Business API access token'
    )
    
    whatsapp_order_template = fields.Char(
        string='Order Notification Template',
        config_parameter='whatsapp.order_template',
        default="Hello {customer_name}! Your order #{order_name} has been confirmed. Total: {amount_total}. Date: {date_order}. Thank you!",
        help='Template for order confirmation message. Available variables: {customer_name}, {order_name}, {amount_total}, {date_order}'
    )
    
    whatsapp_employee_phone = fields.Char(
        string='Employee Phone Number',
        config_parameter='whatsapp.employee_phone',
        help='Phone number of the employee to notify for new orders (with country code, e.g., +1234567890)'
    )
    
    whatsapp_employee_template = fields.Char(
        string='Employee Notification Template',
        config_parameter='whatsapp.employee_template',
        default="🔔 New Order Alert! Customer: {customer_name}, Order: #{order_name}, Amount: {amount_total}, Date: {date_order}, Phone: {customer_phone}. Please process this order.",
        help='Template for employee notification message. Available variables: {customer_name}, {order_name}, {amount_total}, {date_order}, {customer_phone}'
    )