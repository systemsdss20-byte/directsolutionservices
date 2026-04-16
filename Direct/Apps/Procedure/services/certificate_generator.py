import os
from docxtpl import DocxTemplate, RichText
from django.conf import settings

from Direct.Apps.Procedure.pdf_views import generate_pdf_fill

class CertificateGenerator:
    """
    Service class for generating certificates in DOCX format using templates.
    """
    @staticmethod
    def generate_docx(cusname, dot_number, effective_date, drivers):
        filename = f"{cusname.replace(' ', '_')}_RANDOM_POOL.docx"
        path_template = os.path.join(settings.TEMPLATES_PDF, 'CERTIFICADO_DRIVERS_RANDOM.docx')
        doc = DocxTemplate(path_template)
        rt = RichText()
        rt.add(cusname)
        context = {
            'company_name': rt, 
            'effective_date': effective_date.strftime('%B %d, %Y'),
            'dot_number': dot_number, 'drivers': drivers
        }
        doc.render(context)
        directory = os.path.join(settings.FILES_PDF, filename)
        doc.save(directory)
        return directory
    
    
    @staticmethod
    def generate_enrollment_pdf(cusname, effective_date, expiration_date):
        try:
            data = {
                'cusname': cusname, 
                'effective date': effective_date, 
                'expiration date': expiration_date
            }
            file_name = f"{cusname.replace(' ', '_').replace('&', '')}_CERTIFICATE_ENROLLMENT.pdf"
            unique_file_name = generate_pdf_fill('CERTIFICADO_ALCOHOL_DRUG.pdf', data, file_name, flatten=True)
            file_path = os.path.join(settings.FILES_PDF, unique_file_name)
            return file_path
        except Exception as e:
            raise ValueError(f"Error generating enrollment certificate: {e}")
            