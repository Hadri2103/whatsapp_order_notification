# WhatsApp Order Notification - Odoo 18 Module

An Odoo 18 module that automatically sends WhatsApp notifications to customers and employees when orders are confirmed on your ecommerce website.

## Features

- 📱 **Customer Notifications**: Automatic WhatsApp messages sent to customers after order confirmation
- 👨‍💼 **Employee Alerts**: Notifications sent to designated employee for every new order
- 🎨 **Customizable Templates**: Fully configurable message templates for both customers and employees
- 🔧 **Easy Configuration**: Settings integrated into Odoo's Sales configuration panel
- 💳 **Payment Independent**: Works regardless of payment status (paid or unpaid orders)

## Installation

1. Install the Twilio Python SDK:
   ```bash
   pip install twilio
   ```

2. Clone this repository to your Odoo addons directory:
   ```bash
   git clone https://github.com/Hadri2103/whatsapp_order_notification.git
   ```

3. Restart your Odoo server

4. Go to Apps > Update Apps List

5. Search for "WhatsApp Order Notification" and install

## Configuration

1. Go to **Settings > Sales**
2. Scroll down to **"WhatsApp Notifications"** section
3. Configure:
   - **Twilio API Token**: Must be in format `ACCOUNT_SID|AUTH_TOKEN`
   - **WhatsApp From Number**: Your Twilio WhatsApp-enabled phone number
   - **Customer Template SID**: Your approved customer template SID (e.g., HX8264756fadd035142c0905cca6b6b594)
   - **Employee Template SID**: Your approved employee template SID (e.g., HX3e140b59baa66fb67a2172a7442ec2d1)
   - **Employee Phone Number**: Phone number to receive order alerts

## Requirements

- Odoo 18.0
- Python `twilio` package (`pip install twilio`)
- Twilio account with WhatsApp Business API access
- Approved Twilio WhatsApp message templates
- `sale` and `website_sale` modules installed

## Message Variables

### Twilio Template Variables

#### Customer Template Variables (confimundo_order_confirmation_template)
- Variable 1: Customer name
- Variable 2: Order date (YYYY-MM-DD format)
- Variable 3: Total amount with currency

#### Employee Template Variables (confimundo_order_notification_employee)
- Variable 1: Customer name
- Variable 2: Order reference number
- Variable 3: Total amount with currency
- Variable 4: Order date with time (YYYY-MM-DD HH:MM format)
- Variable 5: Customer phone number



## License

This module is licensed under LGPL-3.

## Author

Hadrien Plancq

## Support

For issues and questions, please use the GitHub issue tracker.