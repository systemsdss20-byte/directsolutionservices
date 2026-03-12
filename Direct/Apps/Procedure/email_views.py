import datetime
import os
import json

from django.conf import settings
from django.shortcuts import render
from django.views import View
from xhtml2pdf import pisa

from Direct.Apps.Procedure.services.certificate_generator import CertificateGenerator
from Direct.Apps.Procedure.services.email_services import EmailService
from Direct.Apps.Procedure.services.file_converter import FileConverter

from .models import Invoices, Email_Log, Customers, Drivers
from .pdf_views import GeneratePDF
from ..helpers.message import MessageResponse
from ..helpers.send_email import SendTemplateEmail, validate_email

class SendCertificateRandomTestEmail(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.certificate_generator = CertificateGenerator()      
        self.file_converter = FileConverter()
        self.email_service = EmailService()
        
    def sendCertificates(self,request, customer_id, certificate_date=None):
        try:
            customer = Customers.objects.get(idcustomer=customer_id)
            drivers = Drivers.objects.filter(idcustomer=customer_id, random_test=True, status='Active')
            if certificate_date is None:
                certificate_date =datetime.datetime.now().date()
                if certificate_date.month >= 9:
                    year =  certificate_date.year + 1
                    effective_date = datetime.datetime.strptime('%s-01-01'%year, '%Y-%m-%d').date()
                    expiration_date = datetime.datetime.strptime('%s-12-31'%year, '%Y-%m-%d').date()
                else:
                    effective_date = certificate_date
                    expiration_date = datetime.datetime.strptime('%s-12-31'%certificate_date.year, '%Y-%m-%d').date()
            else:
                certificate_date = datetime.datetime.strptime(str(certificate_date), '%m/%d/%Y').date()
                if certificate_date.month >= 9:
                    year =  certificate_date.year + 1
                    effective_date = datetime.datetime.strptime('%s-01-01'%year, '%Y-%m-%d').date()
                    expiration_date = datetime.datetime.strptime('%s-12-31'%year, '%Y-%m-%d').date()
                else:
                    effective_date = certificate_date
                    expiration_date = datetime.datetime.strptime('%s-12-31'%effective_date.year, '%Y-%m-%d').date()
            if not customer.email:
                return MessageResponse(description='The email is required').error()
            if not validate_email(email=customer.email):
                return MessageResponse(description='The email is not valid').error()
        except ValueError as e:
            print("Error sending certificates parameters:", e)  
            return MessageResponse(description=f"Error sending certificates, please contact the administrator").warning()
        try:
            docx_path = self.certificate_generator.generate_docx(customer.cusname, customer.dotid, effective_date, drivers)
            enrollment_certificate_path = self.certificate_generator.generate_enrollment_pdf(customer.cusname, effective_date, expiration_date)
            random_pool_pdf_path = self.file_converter.convert_docx_to_pdf(docx_path)
            if not os.path.exists(random_pool_pdf_path) or not os.path.exists(enrollment_certificate_path):
                return MessageResponse(description='The file does not exist').error()
            email_result = self.email_service.send_certificates(customer.email, [random_pool_pdf_path, enrollment_certificate_path], user=request.user)
            if email_result['type'] == 'success':
                return MessageResponse(description='Certificates sent successfully', data={'bitexp':expiration_date.strftime('%m/%d/%Y')}).success()
            else:
                return MessageResponse(description='Certificates not sent').error()
        except ValueError as e:
            print("Error sending certificates:", e)  
            return MessageResponse(description=f"Error sending certificates, please contact the administrator").warning()
    
    def get(self, request, *args, **kwargs):        
        return render(
            request, 
            'Procedure/Customers/Applications/DOT/certificate_random_test.html', 
            {
                "customer": Customers.objects.only('idcustomer', 'cusname').get(pk=kwargs['customer_id']),
                "title_certificate_random": 'Certificate Drivers Random Test',
            }
        )
      
    def post(self, request, *args, **kwargs):
        try:            
            customer_id = kwargs['customer_id']
            json_data = json.load(request)
            certificate_date = json_data.get('certificate_date', None)
            if certificate_date is None:
                return MessageResponse(description="The effective date is required").error()
            effective_date = datetime.datetime.strptime(certificate_date, '%m/%d/%Y').date()
            if effective_date.month >= 9:
                year = effective_date.year + 1
                expiration_date = datetime.datetime.strptime('%s-12-31'%year, '%Y-%m-%d').date()
            else:
                expiration_date = datetime.datetime.strptime('%s-12-31'%effective_date.year, '%Y-%m-%d').date()
            customer = Customers.objects.only('bitexp').get(idcustomer=customer_id)
            customer.bitexp = expiration_date
            customer.save()
            return self.sendCertificates(request, customer_id, certificate_date)
        except ValueError as e:
            print("Error sending certificates:", e)
            return MessageResponse(description="Error sending certificates", data={}).error()
          
class Send_invoice_email(View):

    def get(self, request, *args, **kwargs):
        invoice = Invoices.objects.get(idinvoice=self.kwargs['invoice_id'])
        validated_email = False
        try:
            customer = Customers.objects.only('email').get(idcustomer=invoice.idcustomer_id)
            validated_email = validate_email(email=customer.email)
        except Exception as e:
            print(e)
        return render(request, 'Procedure/Customers/Invoices/modal_email.html',
                      {'validated_email': validated_email, 'email': invoice.idcustomer.email,
                       'invoice_id': invoice.idinvoice})

    def post(self, request, *args, **kwargs):
        invoice_id = self.kwargs['invoice_id']
        to_email = json.load(request)['email']
        try:
            html = GeneratePDF.Create_PDF(request, invoice_id)
            invoice = Invoices.objects.get(idinvoice=invoice_id)
            output_filename = "{0}/invoices/{1}/Invoice{2}_{3}.pdf".format(settings.FILES_PDF, invoice.idcustomer_id,
                                                                           invoice.idinvoice,
                                                                           datetime.datetime.today().strftime('%m%d%Y'))
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            with open(output_filename, "w+b") as result_file:
                # convert HTML to PDF
                pisa_status = pisa.CreatePDF(html, dest=result_file)
                result_file.close()
            if not pisa_status.err:
                try:
                    email_is_sent = SendTemplateEmail(
                        template='Signatures/firma.html',
                        subjects='Invoice Notification',
                        recipients=to_email, context={},
                        images=['dss.png', 'whatsapp_logo.png'],
                    ).start(
                        invoice=invoice_id,
                        file=output_filename,
                        user=request.user
                    )
                    if email_is_sent:
                        return MessageResponse(description='Email sent successfully').success()
                    else:
                        return MessageResponse(description='Email not sent').error()
                except Exception as e:
                    print(e)
                    return MessageResponse(description=str(e)).warning()
            else:
                return MessageResponse(description='Server internal error').error()
        except Exception as e:
            print(e)
            return MessageResponse(description=str(e)).error()


class Sent_Emails(View):
    template = "Procedure/Customers/Invoices/list_emails.html"

    def get(self, request, *args, **kwargs):
        emails = Email_Log.objects.filter(invoice__idinvoice=self.kwargs["invoice_id"])
        return render(request, self.template, {'emails': emails})
