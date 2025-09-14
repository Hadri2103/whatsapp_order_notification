import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    whatsapp_sent = fields.Boolean(string='WhatsApp Sent', default=False)

    def write(self, vals):
        """Override write to detect when order status changes to 'sent' (Quotation sent)"""
        result = super(SaleOrder, self).write(vals)
        
        # Check if state changed to 'sent' (Quotation sent) for ecommerce orders
        if ('state' in vals and vals['state'] == 'sent' and 
            self.website_id and not self.whatsapp_sent):
            _logger.info(f"Ecommerce order status changed to 'Quotation sent': {self.name} - triggering WhatsApp notifications")
            self._send_whatsapp_notification()
            self._send_employee_notification()
        
        return result

    def action_confirm(self):
        """Override to send WhatsApp notification after order confirmation (fallback for other cases)"""
        result = super(SaleOrder, self).action_confirm()
        
        # Fallback: Send WhatsApp notification for ecommerce orders if not sent yet
        if self.website_id and not self.whatsapp_sent:
            _logger.info(f"Order confirmation - sending WhatsApp for {self.name}")
            self._send_whatsapp_notification()
            self._send_employee_notification()
        
        return result

    def _send_whatsapp_notification(self):
        """Send WhatsApp notification to customer using Twilio SDK"""
        try:
            _logger.info(f"Starting WhatsApp notification process for order {self.name}")
            
            # Get WhatsApp configuration
            config = self.env['ir.config_parameter'].sudo()
            api_token = config.get_param('whatsapp.api_token')
            customer_template_sid = config.get_param('whatsapp.customer_template_sid')
            from_number = config.get_param('whatsapp.from_number')
            
            if not api_token:
                _logger.warning("WhatsApp API token missing")
                return False
            
            if not customer_template_sid:
                _logger.warning("Twilio customer template SID missing")
                return False
            
            # Get customer phone number
            phone = self._get_customer_phone()
            _logger.info(f"Customer phone: {phone if phone else 'NOT FOUND'}")
            
            if not phone:
                _logger.warning(f"No phone number found for customer {self.partner_id.name}")
                return False
            
            # Send WhatsApp message to customer using Twilio SDK
            success = self._send_twilio_customer_template_message(api_token, phone, customer_template_sid, from_number)
            
            if success:
                self.whatsapp_sent = True
                _logger.info(f"WhatsApp notification sent for order {self.name}")
            
            return success
            
        except Exception as e:
            _logger.error(f"Error sending WhatsApp notification for order {self.name}: {str(e)}")
            return False

    def action_send_whatsapp_manual(self):
        """Manual action to send WhatsApp notifications (for testing)"""
        for order in self:
            if order.website_id:
                _logger.info(f"Manual WhatsApp trigger for order {order.name}")
                order.whatsapp_sent = False  # Reset to allow resending
                order._send_whatsapp_notification()
                order._send_employee_notification()
            else:
                _logger.warning(f"Order {order.name} is not a website order")
        return True

    def _get_customer_phone(self):
        """Get customer phone number in international format"""
        phone = None
        
        # Try different phone field names that might exist in Odoo 18
        if hasattr(self.partner_id, 'phone') and self.partner_id.phone:
            phone = self.partner_id.phone
        elif hasattr(self.partner_id, 'mobile') and self.partner_id.mobile:
            phone = self.partner_id.mobile
        
        if not phone:
            _logger.warning(f"No phone field found for partner {self.partner_id.name}. Available fields: {[f for f in self.partner_id._fields.keys() if 'phone' in f.lower() or 'mobile' in f.lower()]}")
            return False
        
        # Clean phone number (remove spaces, dashes, etc.)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (assuming default country)
        if not phone.startswith('1') and len(phone) == 10:  # US format example
            phone = '1' + phone
        
        return phone



    def _send_employee_notification(self):
        """Send WhatsApp notification to employee about new order using Twilio SDK"""
        try:
            # Get WhatsApp configuration
            config = self.env['ir.config_parameter'].sudo()
            api_token = config.get_param('whatsapp.api_token')
            employee_phone = config.get_param('whatsapp.employee_phone')
            employee_template_sid = config.get_param('whatsapp.employee_template_sid')
            from_number = config.get_param('whatsapp.from_number')
            
            if not api_token or not employee_phone:
                _logger.warning("WhatsApp employee notification configuration missing")
                return False
            
            if not employee_template_sid:
                _logger.warning("Twilio employee template SID missing for employee notification")
                return False
            
            # Clean employee phone number
            employee_phone = self._clean_phone_number(employee_phone)
            if not employee_phone:
                _logger.warning("Invalid employee phone number format")
                return False
            
            # Send WhatsApp message to employee using Twilio SDK
            success = self._send_twilio_employee_template_message(api_token, employee_phone, employee_template_sid, from_number)
            
            if success:
                _logger.info(f"Employee notification sent for order {self.name}")
            
            return success
            
        except Exception as e:
            _logger.error(f"Error sending employee notification for order {self.name}: {str(e)}")
            return False

    def _clean_phone_number(self, phone):
        """Clean and format phone number"""
        if not phone:
            return False
        
        # Remove all non-digit characters except +
        phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Remove + if present and ensure it starts with country code
        if phone.startswith('+'):
            phone = phone[1:]
        
        return phone if phone else False
    
    def _get_customer_template_variables(self):
        """Get template variables for customer Twilio template"""
        import json
        
        # Customer template variables: 1: client name, 2: date, 3: amount
        variables = {
            "1": self.partner_id.name,  # Customer name
            "2": self.date_order.strftime('%Y-%m-%d'),  # Date
            "3": f"{self.amount_total:.2f} {self.currency_id.name}",  # Amount
        }
        
        return json.dumps(variables)
    
    def _get_employee_template_variables(self):
        """Get template variables for employee Twilio template"""
        import json
        
        # Employee template variables: 1: client name, 2: order reference, 3: amount, 4: date, 5: phone number
        variables = {
            "1": self.partner_id.name,  # Customer name
            "2": self.name,  # Order number
            "3": f"{self.amount_total:.2f} {self.currency_id.name}",  # Amount
            "4": self.date_order.strftime('%Y-%m-%d %H:%M'),  # Date
            "5": self.partner_id.phone or self.partner_id.mobile or 'Not provided'  # Customer phone
        }
        
        return json.dumps(variables)
    
    def _send_twilio_customer_template_message(self, api_token, phone, template_sid, from_number=None):
        """Send WhatsApp message to customer using Twilio SDK with template"""
        try:
            from twilio.rest import Client
            
            # Extract Account SID and Auth Token
            if '|' in api_token:
                account_sid, auth_token = api_token.split('|')
            else:
                _logger.error("API token must be in format ACCOUNT_SID|AUTH_TOKEN for Twilio SDK")
                return False
            
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Format phone numbers for WhatsApp
            to_number = f'whatsapp:+{phone}' if not phone.startswith('+') else f'whatsapp:{phone}'
            from_number = f'whatsapp:{from_number}' if from_number else 'whatsapp:+14155238886'
            
            # Prepare customer template variables
            content_variables = self._get_customer_template_variables()
            
            _logger.info(f"Sending customer Twilio template message to {to_number} with template {template_sid}")
            _logger.info(f"Customer template variables: {content_variables}")
            
            # Send message using Twilio SDK
            message = client.messages.create(
                content_sid=template_sid,
                to=to_number,
                from_=from_number,
                content_variables=content_variables
            )
            
            _logger.info(f"Customer Twilio message sent successfully. SID: {message.sid}")
            return True
            
        except ImportError:
            _logger.error("Twilio SDK not installed. Please install with: pip install twilio")
            return False
        except Exception as e:
            _logger.error(f"Error sending customer Twilio template message: {str(e)}")
            return False
    
    def _send_twilio_employee_template_message(self, api_token, phone, template_sid, from_number=None):
        """Send WhatsApp message to employee using Twilio SDK with template"""
        try:
            from twilio.rest import Client
            
            # Extract Account SID and Auth Token
            if '|' in api_token:
                account_sid, auth_token = api_token.split('|')
            else:
                _logger.error("API token must be in format ACCOUNT_SID|AUTH_TOKEN for Twilio SDK")
                return False
            
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Format phone numbers for WhatsApp
            to_number = f'whatsapp:+{phone}' if not phone.startswith('+') else f'whatsapp:{phone}'
            from_number = f'whatsapp:{from_number}' if from_number else 'whatsapp:+14155238886'
            
            # Prepare employee template variables
            content_variables = self._get_employee_template_variables()
            
            _logger.info(f"Sending employee Twilio template message to {to_number} with template {template_sid}")
            _logger.info(f"Employee template variables: {content_variables}")
            
            # Send message using Twilio SDK
            message = client.messages.create(
                content_sid=template_sid,
                to=to_number,
                from_=from_number,
                content_variables=content_variables
            )
            
            _logger.info(f"Employee Twilio message sent successfully. SID: {message.sid}")
            return True
            
        except ImportError:
            _logger.error("Twilio SDK not installed. Please install with: pip install twilio")
            return False
        except Exception as e:
            _logger.error(f"Error sending employee Twilio template message: {str(e)}")
            return False