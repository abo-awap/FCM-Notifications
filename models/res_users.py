import firebase_admin
from firebase_admin import credentials, messaging
from odoo import models, fields, api
from odoo.modules.module import get_module_resource

class ResUsers(models.Model):
    _inherit = 'res.users'

    fcm_token = fields.Char(string='FCM Token', index=True)

    def _get_firebase_app(self):
        try:
            return firebase_admin.get_app()
        except ValueError:
            path = get_module_resource('fcm_notifications', 'data', 'firebase_key.json')
            cred = credentials.Certificate(path)
            return firebase_admin.initialize_app(cred)

    def send_device_notification(self, title, body):
        if not self.fcm_token:
            return False
            
        self._get_firebase_app()

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=self.fcm_token,
        )

        try:
            response = messaging.send(message)
            print(f"✅ Successfully sent message: {response}")
            return True
        except Exception as e:
            print(f"❌ Firebase Error Detailed: {e}")
            return False