import datetime
import time
import os
from email.mime.image import MIMEImage
import threading
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..Procedure.models import Email_Log, Invoices, User
from dotenv import load_dotenv
load_dotenv()
class SendTemplateEmail():
    def __init__(self, template, subjects, images, context, recipients, **kwargs):
        self.template = template
        self.images = images
        self.subjects = subjects
        self.context = context
        self.recipients = recipients
        self.kwargs = kwargs

    def start(self, **kwargs):
        try:   
            thread = threading.Thread(target=self.process_email(**kwargs))
            thread.start()
            return True
        except threading.ThreadError as te:
            print(f"Error starting thread: {te}")
            return False
        except ValueError as e:
            print(f"An unexpected error occurred while processing the email: {e}")
            return False
        except RuntimeError as ve:
            print(f"Error sending email: {ve}")
            return False
            
    
    def process_email(self, **kwargs):
        sent = False
        self.kwargs = kwargs
        try:
            if type(self.recipients) is not list:
                if validate_email(self.recipients):
                    sent = self.__send(recipient=self.recipients, subject=self.subjects, context=self.context)
                self.saveEmailLog(sent, self.recipients, self.subjects, **kwargs)
            else:
                email_sent = 0
                for recipient in self.recipients:
                    if email_sent == 28:
                        time.sleep(120)
                        email_sent = 0
                    subject = self.subjects.pop() if type(self.subjects) is list else self.subjects
                    if validate_email(recipient):
                        sent = self.__send(
                            recipient=recipient,
                            subject=subject,
                            context=self.context.pop() if type(self.context) is list else self.context
                        )
                    self.saveEmailLog(sent, recipient, subject, **kwargs)
                    email_sent += 1
        except Exception as e:
            raise ValueError(f"Error sending email: {e}")


    def saveEmailLog(self, sent, recipient, subject, **kwargs):
        try:
            email_log = Email_Log()
            email_log.sent = sent
            email_log.subject = subject
            email_log.email = recipient
            email_log.sending_date = datetime.datetime.today()
            if 'invoice' in kwargs.keys():
                email_log.invoice = Invoices.objects.get(idinvoice=kwargs['invoice'])
                email_log.user = kwargs['user']
            else:
                email_log.user = User.objects.get(pk=40)
            email_log.save()
        except Exception as e:
            raise ValueError(f"Error saving email log: {e}")


    def __send(self, recipient, subject, context):
        try:
            from_email = f'Direct Solution Services<{os.environ.get("EMAIL_HOST_USER")}>'
            html_message = render_to_string(self.template, context)
            plain_message = strip_tags(html_message)
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=['%s'%recipient], headers={'X-Unsent': '1'}
            )
            email.attach_alternative(html_message, 'text/html')
            email.mixed_subtype = 'related'

            for image in self.images:
                image_path = finders.find('site/img/email/%s'%image)
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                img = MIMEImage(image_data)
                img.add_header('Content-ID', '<%s>'%image)
                img.add_header('Content-Disposition', 'inline', filename='%s'%image)
                email.attach(img)

            if 'file' in self.kwargs:
                if type(self.kwargs['file']) is list:
                    for f in self.kwargs['file']:
                        email.attach_file(f)
                else:
                    email.attach_file(self.kwargs['file'])

            is_send = email.send(fail_silently=False)
            return is_send
        except Exception as e:
            print(e)
            return False


def validate_email(email):
    expressions = ['NONE@', 'NOTIENE', '@N.COM', '@NA.COM', 'NONE', 'NN@NN.COM', 'N/A@GMAIL.COM']
    check_email = email.upper()
    if any(expression in check_email for expression in expressions):
        return False
    return True


