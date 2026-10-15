import logging
from odoo import models, api, tools, _

_logger = logging.getLogger(__name__)

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=None, **kwargs):
        # doing the official odoo job 
        res = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)

        recipients = self.env['res.partner']

        # get users
        if message.model == 'discuss.channel' and message.res_id:
            channel = self.env['discuss.channel'].sudo().browse(message.res_id)
            recipients = channel.channel_member_ids.mapped('partner_id')
        else:
            notifications = self.env['mail.notification'].sudo().search([
                ('mail_message_id', '=', message.id)
            ])
            recipients = notifications.mapped('res_partner_id')

        # fiter // not me and not how has no fcm token
        author_id = message.author_id.id
        final_recipients = recipients.filtered(lambda p: p.id != author_id)

        for partner in final_recipients:
            user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            
            if user and user.fcm_token:
                title = message.author_id.name or "إشعار جديد"
                body = tools.html2plaintext(message.body) if message.body else "وصلتك رسالة جديدة"
                user.sudo().send_device_notification(title, body)

        return res