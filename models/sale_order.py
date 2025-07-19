import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    whatsapp_sent = fields.Boolean(string='WhatsApp Sent', default=False)

    def action_confirm(self):
        """Override to send WhatsApp notification after order confirmation"""
        result = super(SaleOrder, self).action_confirm()
        
        # Send WhatsApp notification for ecommerce orders
        if self.website_id and not self.whatsapp_sent:
            self._send_whatsapp_notification()
            self._send_employee_notification()
        
        return result

    def _send_whatsapp_notification(self):
        """Send WhatsApp notification to customer"""
        try:
            # Get WhatsApp configuration
            config = self.env['ir.config_parameter'].sudo()
            api_url = config.get_param('whatsapp.api_url')
            api_token = config.get_param('whatsapp.api_token')
            
            if not api_url or not api_token:
                _logger.warning("WhatsApp API configuration missing")
                return False
            
            # Get customer phone number
            phone = self._get_customer_phone()
            if not phone:
                _logger.warning(f"No phone number found for customer {self.partner_id.name}")
                return False
            
            # Prepare message
            message = self._prepare_whatsapp_message()
            
            # Send WhatsApp message
            success = self._send_whatsapp_message(api_url, api_token, phone, message)
            
            if success:
                self.whatsapp_sent = True
                _logger.info(f"WhatsApp notification sent for order {self.name}")
            
            return success
            
        except Exception as e:
            _logger.error(f"Error sending WhatsApp notification for order {self.name}: {str(e)}")
            return False

    def _get_customer_phone(self):
        """Get customer phone number in international format"""
        phone = self.partner_id.phone or self.partner_id.mobile
        if not phone:
            return False
        
        # Clean phone number (remove spaces, dashes, etc.)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (assuming default country)
        if not phone.startswith('1') and len(phone) == 10:  # US format example
            phone = '1' + phone
        
        return phone

    def _prepare_whatsapp_message(self):
        """Prepare WhatsApp message content"""
        template = self.env['ir.config_parameter'].sudo().get_param(
            'whatsapp.order_template',
            """Hello {customer_name}!

Your order #{order_name} has been confirmed.

Order Details:
- Total Amount: {amount_total}
- Order Date: {date_order}

Thank you for your purchase!"""
        )
        
        return template.format(
            customer_name=self.partner_id.name,
            order_name=self.name,
            amount_total=f"{self.amount_total:.2f} {self.currency_id.name}",
            date_order=self.date_order.strftime('%Y-%m-%d %H:%M')
        )

    def _send_whatsapp_message(self, api_url, api_token, phone, message):
        """Send message via WhatsApp API"""
        try:
            # Check if using Twilio API
            if 'twilio.com' in api_url:
                return self._send_twilio_message(api_url, api_token, phone, message)
            else:
                return self._send_meta_message(api_url, api_token, phone, message)
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"WhatsApp API request failed: {str(e)}")
            return False

    def _send_twilio_message(self, api_url, api_token, phone, message):
        """Send message via Twilio WhatsApp API"""
        try:
            import base64
            
            # Extract Account SID from URL or use api_token format
            if '|' in api_token:
                account_sid, auth_token = api_token.split('|')
            else:
                # Assume api_token is auth_token and extract SID from URL
                account_sid = api_url.split('/Accounts/')[1].split('/')[0]
                auth_token = api_token
            
            # Twilio API endpoint
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            # Basic Auth for Twilio
            credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Format phone numbers for WhatsApp
            from_number = 'whatsapp:+14155238886'  # Twilio Sandbox number
            to_number = f'whatsapp:{phone}' if not phone.startswith('whatsapp:') else phone
            
            data = {
                'From': from_number,
                'To': to_number,
                'Body': message
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
            if response.status_code in [200, 201]:
                _logger.info(f"Twilio WhatsApp message sent successfully")
                return True
            else:
                _logger.error(f"Twilio API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            _logger.error(f"Twilio WhatsApp API error: {str(e)}")
            return False

    def _send_meta_message(self, api_url, api_token, phone, message):
        """Send message via Meta WhatsApp API"""
        try:
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(api_url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                _logger.error(f"Meta WhatsApp API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            _logger.error(f"Meta WhatsApp API error: {str(e)}")
            return False

    def _send_employee_notification(self):
        """Send WhatsApp notification to employee about new order"""
        try:
            # Get WhatsApp configuration
            config = self.env['ir.config_parameter'].sudo()
            api_url = config.get_param('whatsapp.api_url')
            api_token = config.get_param('whatsapp.api_token')
            employee_phone = config.get_param('whatsapp.employee_phone')
            
            if not api_url or not api_token or not employee_phone:
                _logger.warning("WhatsApp employee notification configuration missing")
                return False
            
            # Clean employee phone number
            employee_phone = self._clean_phone_number(employee_phone)
            if not employee_phone:
                _logger.warning("Invalid employee phone number format")
                return False
            
            # Prepare employee message
            message = self._prepare_employee_message()
            
            # Send WhatsApp message to employee
            success = self._send_whatsapp_message(api_url, api_token, employee_phone, message)
            
            if success:
                _logger.info(f"Employee notification sent for order {self.name}")
            
            return success
            
        except Exception as e:
            _logger.error(f"Error sending employee notification for order {self.name}: {str(e)}")
            return False

    def _prepare_employee_message(self):
        """Prepare WhatsApp message content for employee"""
        template = self.env['ir.config_parameter'].sudo().get_param(
            'whatsapp.employee_template',
            """🔔 New Order Alert!

Customer: {customer_name}
Order: #{order_name}
Amount: {amount_total}
Date: {date_order}
Phone: {customer_phone}

Please process this order."""
        )
        
        customer_phone = self.partner_id.phone or self.partner_id.mobile or 'Not provided'
        
        return template.format(
            customer_name=self.partner_id.name,
            order_name=self.name,
            amount_total=f"{self.amount_total:.2f} {self.currency_id.name}",
            date_order=self.date_order.strftime('%Y-%m-%d %H:%M'),
            customer_phone=customer_phone
        )

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