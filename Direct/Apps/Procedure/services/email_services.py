from Direct.Apps.helpers.send_email import SendTemplateEmail


class EmailService:
    def send_certificates(self, recipient_email, file_paths, user=None):
        try:
            email_is_sent = SendTemplateEmail(
                template='Signatures/firma.html',
                subjects='Certificates Complance Notification',
                recipients=recipient_email,
                context={},
                images=['dss.png', 'whatsapp_logo.png'],
            ).start(user=user, file=file_paths)
            
            if email_is_sent:
                return {'description': 'Email sent successfully', 'type': 'success'}
            else:
                return {'description': 'Email not sent', 'type': 'error'}
        except Exception as e:
            return {'description': str(e), 'type': 'warning'}