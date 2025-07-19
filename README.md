# WhatsApp Order Notification - Odoo 18 Module

An Odoo 18 module that automatically sends WhatsApp notifications to customers and employees when orders are confirmed on your ecommerce website.

## Features

- 📱 **Customer Notifications**: Automatic WhatsApp messages sent to customers after order confirmation
- 👨‍💼 **Employee Alerts**: Notifications sent to designated employee for every new order
- 🎨 **Customizable Templates**: Fully configurable message templates for both customers and employees
- 🔧 **Easy Configuration**: Settings integrated into Odoo's Sales configuration panel
- 💳 **Payment Independent**: Works regardless of payment status (paid or unpaid orders)

## Installation

1. Clone this repository to your Odoo addons directory:
   ```bash
   git clone https://github.com/Hadri2103/whatsapp_order_notification.git
   ```

2. Restart your Odoo server

3. Go to Apps > Update Apps List

4. Search for "WhatsApp Order Notification" and install

## Configuration

1. Go to **Settings > Sales**
2. Scroll down to **"WhatsApp Notifications"** section
3. Configure:
   - **WhatsApp API URL**: Your WhatsApp Business API endpoint
   - **WhatsApp API Token**: Your access token
   - **Employee Phone Number**: Phone number to receive order alerts
   - **Message Templates**: Customize customer and employee messages

## Requirements

- Odoo 18.0
- WhatsApp Business API access
- `sale` and `website_sale` modules installed

## Message Variables

### Customer Messages
- `{customer_name}` - Customer's name
- `{order_name}` - Order number
- `{amount_total}` - Total amount with currency
- `{date_order}` - Order date

### Employee Messages
- All customer variables plus:
- `{customer_phone}` - Customer's phone number

## License

This module is licensed under LGPL-3.

## Author

Hadrien Plancq

## Support

For issues and questions, please use the GitHub issue tracker.