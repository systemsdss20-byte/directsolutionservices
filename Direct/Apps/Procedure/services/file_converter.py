import pythoncom
from docx2pdf import convert

class FileConverter:
    """
    Service for converting files between different formats
    """
    def convert_docx_to_pdf(self, docx_path):
        pdf_path = docx_path.replace('.docx', '.pdf')
        pythoncom.CoInitialize()
        convert(docx_path, pdf_path)
        pythoncom.CoUninitialize()
        return pdf_path