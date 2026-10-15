from odoo import http
from odoo.http import request
import json

class FcmController(http.Controller):

    @http.route('/api/fcm/update_token',type='http',auth='user',methods=['POST'],csrf=False)
    def update_fcm_token(self,**kwargs):
        try:
            data = json.loads(request.httprequest.data)
            fcm_token = data.get('fcm_token')
            user = request.env.user
            if fcm_token:
                user.sudo().write({'fcm_token':fcm_token})
                return request.make_response(
                    json.dumps({'status' : 'success', 'message': 'Token updated successfully for user: %s' % request.env.user.name}),
                    headers=[('Content-Type', 'application/json')]
                )
            return request.make_response(
                    json.dumps({'status' : 'error', 'message': 'Token Not Provided'}),
                    headers=[('Content-Type', 'application/json')]
                )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
    
    @http.route('/api/fcm/remove_token', type='json', auth='public', methods=['POST'])
    def delete_fcm_token(self):
        request.env.user.sudo().write({'fcm_token':False})
        return {'status': 'success', 'message': 'Token removed'}
    
    @http.route('/api/fcm/update_and_test', type='json', auth='user', methods=['POST'], csrf=False)
    def update_and_test_token(self, fcm_token=None):
        
        if not fcm_token:
            return {'status': 'error', 'message': 'Missing token'}

        # 1. حفظ التوكن أولاً
        user = request.env.user
        user.sudo().write({'fcm_token': fcm_token})

        # 2. استدعاء دالة الإرسال فوراً للتجربة
        # سنرسل إشعاراً لنفس المستخدم الذي أرسل التوكن
        success = user.sudo().send_device_notification(
            "اختبار الاتصال", 
            "إذا وصلك هذا الإشعار، فالمكتبات وإعدادات فيربيس صحيحة 100%"
        )

        if success:
            return {
                'status': 'success',
                'message': f'Token updated and notification sent to {user.name}'
            }
        else:
            return {
                'status': 'error',
                'message': 'Token updated but Firebase failed. Check Odoo logs!'
            }