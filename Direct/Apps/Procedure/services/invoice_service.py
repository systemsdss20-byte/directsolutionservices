from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class InvoiceService:
    """Maneja la lógica de creación de facturas"""
    
    # Constantes
    ROAD_TAX_SERVICES = {'158', '216'}
    
    def __init__(self):
        self.invoice = None
        self.user = None
    
    @transaction.atomic
    def create_invoice(self, form, formset, user, customer_id, project_id, post_data):
        """
        Crea una factura con validación completa.
        
        Args:
            form: InvoiceForm validado
            formset: InvoicesDetFormSet validado
            user: Usuario actual
            customer_id: ID del cliente
            project_id: ID del proyecto (0 si no existe)
            post_data: Datos del POST
            
        Returns:
            dict con resultado de la operación
            
        Raises:
            ValidationError: Si hay error en validación
        """
        try:
            self.user = user
            
            # 1. Crear factura
            self.invoice = form.customSave(user.id, post_data.get("amount"))
            
            # 2. Procesar detalles
            total_amount = self._process_invoice_details(
                formset.save(commit=False), 
                customer_id, 
                project_id, 
                post_data
            )
            
            # 3. Actualizar total
            self._update_invoice_amount(total_amount)
            
            return {
                'success': True,
                'data': {
                    'idinvoice': self.invoice.idinvoice,
                    'amount': total_amount
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}", exc_info=True)
            if self.invoice:
                self.invoice.delete()
            raise ValidationError(f"Error creating invoice: {str(e)}")
    
    def _process_invoice_details(self, invoice_details, customer_id, project_id, post_data):
        """Procesa cada detalle de la factura"""
        total_amount = 0
        
        # Optimizar: traer servicios en una sola query
        service_ids = [detail.code.idservice for detail in invoice_details]
        services = self._get_services(service_ids)
        
        for index, detail in enumerate(invoice_details):
            detail.save()
            total_amount += detail.amount
            
            service = services.get(detail.code.idservice)
            if not service:
                raise ValidationError(f"Service not found: {detail.code.idservice}")
            
            # Actualizar proyecto existente
            if project_id and not service.need_invoice:
                self._update_project(project_id, detail)
            
            # Crear nuevo proyecto si es necesario
            elif service.is_project and not project_id:
                self._create_project(service, detail, customer_id, index, post_data)
        
        return total_amount
    
    def _create_project(self, service, detail, customer_id, index, post_data):
        """Crea un nuevo proyecto en base al detalle"""
        project_data = {
            'idinvoicedet': detail,
            'quantity': detail.quantity,
            'service': service,
            'invoice': self.invoice,
            'service_name': detail.service,
            'comments': self._get_project_comments(service, index, post_data),
            'status': 'Opened',
            'request': date.today(),
            'iduser': self.user,
            'statuslast': date.today(),
            'iduserlast': self.user,
            'idcustomer_id': customer_id,
        }
        
        project = Projects.objects.create(**project_data)
        
        # Crear nota si existe
        note_text = post_data.get(f'details-{index}-comments_notes')
        if note_text:
            NotesProjects.objects.create(
                iduser=self.user,
                comments=note_text,
                project=project
            )
    
    def _get_project_comments(self, service, index, post_data):
        """Obtiene comentarios del proyecto"""
        if service.idservice not in self.ROAD_TAX_SERVICES:
            return post_data.get(f'details-{index}-coments', '')
        
        # Lógica para servicios de road tax
        return post_data.get(f'details-{index}-comments_projects', '')
    
    def _update_project(self, project_id, detail):
        """Actualiza un proyecto existente"""
        Projects.objects.filter(idproject=project_id).update(
            invoice=self.invoice,
            idinvoicedet=detail
        )
    
    def _update_invoice_amount(self, total_amount):
        """Actualiza el monto total de la factura"""
        if self.invoice.amount != total_amount:
            self.invoice.amount = round(total_amount, 2)
            self.invoice.deu = round(total_amount, 2)
            self.invoice.save()
    
    @staticmethod
    def _get_services(service_ids):
        """Obtiene servicios en una sola query (evita N+1)"""
        return {
            service.idservice: service 
            for service in Services.objects.filter(idservice__in=service_ids)
        }


# views.py
@login_required(login_url='Procedure:login')
def add_customers_invoice(request, customer_id, project_id):
    """Vista para agregar factura. Delega lógica a servicio"""
    
    if request.method == "POST":
        return _handle_invoice_post(request, customer_id, project_id)
    else:
        return _handle_invoice_get(request, customer_id, project_id)


def _handle_invoice_post(request, customer_id, project_id):
    """Procesa POST de factura"""
    form = InvoiceForm(request.POST)
    
    if not form.is_valid():
        return _error_response("Form validation failed", form.errors, 500)
    
    formset = InvoicesDetFormSet(request.POST, instance=form.instance)
    
    if not formset.is_valid():
        logger.warning(f"Formset validation failed: {formset.errors}")
        return _error_response("Detail validation failed", formset.errors, 500)
    
    try:
        service = InvoiceService()
        result = service.create_invoice(
            form, formset, request.user, customer_id, project_id, request.POST
        )
        return _success_response(result['data'])
        
    except ValidationError as e:
        return _error_response(str(e), {}, 500)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _error_response("Unexpected error during invoice creation", {}, 500)


def _handle_invoice_get(request, customer_id, project_id):
    """Procesa GET de factura"""
    customer = Customers.objects.only(
        "idcustomer", "cusname", "address"
    ).get(pk=customer_id)
    
    formset = _get_initial_formset(project_id)
    next_invoice = Invoices.objects.latest("idinvoice")
    
    template = (
        'Procedure/Customers/Invoices/modal-invoice.html' 
        if project_id 
        else 'Procedure/Customers/Invoices/invoice.html'
    )
    
    return render(request, template, {
        'form': InvoiceForm(),
        'formset': formset,
        'customer': customer,
        'customer_id': customer.idcustomer,
        'datetoday': date.today().strftime("%m/%d/%Y"),
        'project_id': project_id,
        'idinvoice': next_invoice.idinvoice + 1
    })


def _get_initial_formset(project_id):
    """Obtiene formset inicial según proyecto"""
    if not project_id:
        return InvoicesDetFormSet()
    
    project = Projects.objects.get(idproject=project_id)
    return InvoicesDetFormSet(initial=[{
        'code': project.service.idservice,
        'service': project.service_name,
        'cost': project.service.cost,
        'rate': project.service.rate,
        'coments': project.comments,
        'quantity': project.quantity,
        'amount': project.service.rate
    }])


def _success_response(data):
    """Response exitoso"""
    return HttpResponse(
        JsonResponse({
            "message": {
                'description': 'Invoice saved successfully',
                'type': 'success'
            },
            "data": data
        }),
        content_type="application/json",
        status=200
    )


def _error_response(description, errors, status_code):
    """Response de error"""
    return HttpResponse(
        JsonResponse({
            "message": {
                'description': description,
                'type': 'error'
            },
            'errors': errors
        }),
        content_type='application/json',
        status=status_code
    )