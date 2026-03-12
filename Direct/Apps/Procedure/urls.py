
from django.conf.urls.static import static
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import path, re_path, include
from . import views, pdf_views, views_reports, docx_view
from .docx_view import Certificate_random_test, Certificate_Alcohol_Drugs, Certificate_Alcohol
from .email_views import SendCertificateRandomTestEmail, Send_invoice_email, Sent_Emails
from .pdf_views import Certificate_Enrollment_Alcohol_Drug
from .tables_views import SalesDetails, InvoicesDatatable, CustomerFilesTable, NewsTable, ServicesTable, UnitsDatatable, \
    InvoicesUnpaidDatatable, CardsDatatable, CustomersTable, DriversDatatable
from .views import ProjectsView, CardView, ServicesView
from .views_reports import Sellers, Invoice_Unpaid
from ..helpers.update_dot import UpdateDot

app_name = 'Procedure'
from ... import settings

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('index/', views.index, name='index'),
    path('openlinks/', views.open_links),
    path('customer/', permission_required('Procedure.add_customers', 'Procedure:index')(views.add_customers), name='customer'),
    path('customer_add/', permission_required('Procedure.add_customers', 'Procedure:index')(views.add_customers), name='customer_add'),
    path('customers/', permission_required('Procedure.list_customers', 'Procedure:index')(views.list_customers), name='customers'),
    path('customer_datatable/', permission_required('Procedure.list_customers', 'Procedure:index')(CustomersTable.as_view())),
    path('customer_view/<int:customer_id>', permission_required('Procedure.view_customers', 'Procedure:index')(
        views.view_customer), name='customer_view'),
    re_path(r'^customer_edit/(?P<customer_id>\d+)/$',
                      permission_required('Procedure.change_customers', 'Procedure:index')(views.edit_customer),
                      name='customer_edit'),
    path('delete_customer/', permission_required('Procedure.delete_customers', 'Procedure:index')(
        views.delete_customer), name='delete_customer'), # type: ignore

    path('units/<int:customer_id>', permission_required('Procedure.view_units', 'Procedure:index')(views.list_units), name='units'),
    path('units_datatable/', login_required(UnitsDatatable.as_view(), login_url='Procedure:login'), name='datatable_units'),
    path('unit_add/<int:customer_id>', permission_required('Procedure.add_units', 'Procedure:index')(
        views.add_customers_unit), name='unit'),
    path('view_unit/<int:unit_id>', permission_required('Procedure.view_units', 'Procedure:index')(
        views.view_customer_unit)),
    path('unit_edit/<int:unit_id>', permission_required('Procedure.change_units', 'Procedure:index')(
        views.edit_customer_unit), name='unit_edit'),
    path('unit_delete/', permission_required('Procedure.delete_units', 'Procedure:index')(views.delete_customer_unit), name='unit_delete'),
    path('change_status_unit/', permission_required('Procedure.change_status_units', 'Procedure:index')(
        views.change_status_units), name='cunit'),
    path('update_date_road_taxes/<int:unit_id>', permission_required('Procedure.change_units', 'Procedure:index')(
        views.edit_customer_unit)),
    path('search_unit/', login_required(views.search_by_vin, login_url='Procedure:login')),
    path('invoice_add/<int:customer_id>/<int:project_id>/', permission_required('Procedure.add_invoices', 'Procedure:index')(
        views.add_customers_invoice), name='invoice'),
    path('get_service/', views.get_services, name='get_service'),
    path('delete_invoice/', permission_required('Procedure.delete_invoices', 'Procedure:index')(views.delete_invoice), name='delete_paid'),
    path('paid/<int:idinvoice>', permission_required('Procedure.add_invoice_paid', 'Procedure:index')(views.paid), name='paid'),
    path('paids/<int:idinvoice>', permission_required('Procedure.view_invoice_paid', 'Procedure:index')(
        views.list_paids), name='list_paid'),
    path('edit_paid/<int:idpaid>', permission_required('Procedure.change_invoice_paid', 'Procedure:index')(
        views.edit_paid), name='edit_paid'),
    # pdf
    path('pdf_invoice/<int:idinvoice>', views.pdf_invoice, name='pdf_invoice'),
    path('pdfInvoice/<int:idinvoice>', pdf_views.view_invoice, name='view_invoice'),
    path('fueltaxes/<int:customer_id>', permission_required('Procedure.list_millages', 'Procedure:index')(
        views.list_fueltaxes), name='fuel_taxes'),
    path('add_fueltaxes/<int:idcustomer>', permission_required('Procedure.add_millages', 'Procedure:index')(
        views.add_fueltaxes), name='add_fuel_taxes'),
    path('view_fueltaxes/<int:idmillage>', permission_required('Procedure.view_millages', 'Procedure:index')(
        views.view_fueltaxes), name='view_fuel_taxes'),
    path('edit_fueltaxes/<int:idmillage>', permission_required('Procedure.change_millages', 'Procedure:index')(
        views.edit_fueltaxes), name='edit_fuel_taxes'),
    path('invoices/<int:customer_id>', login_required(views.InvoicesDetails.as_view(), login_url='Procedure:login'), name='invoices'),
    path('datatable_invoices_details/', login_required(InvoicesDatatable.as_view(), login_url='Procedure:login'), name='invoices'),
    path('datatable_invoices_unpaid/', login_required(InvoicesUnpaidDatatable.as_view(), login_url='Procedure:login'), name='invoices'),
    path('list_recives/', views.list_recive, name='list_recives'),
    path('list_recives_summary/', views.list_recive_summary, name='list_recives_summary'),
    path('showform_recives/<int:customer_id>', views.add_recive, name='showform_recives'),
    path('add_recives/<int:customer_id>', views.add_recive, name='add_recives'),
    path('delete_recives/', views.delete_recive, name='delete_recives'),
    path('pdf_recive/', pdf_views.pdf_recive, name='pdf_recive'),
    path('ShowCoverPDF/<int:customer_id>', views.cover_page, name='ShowCoverPDF'),
    path('GenerateCoverPDF/<int:customer_id>', pdf_views.cover_pdf, name='GenerateCoverPDF'),
    path('Scheduleb/', pdf_views.scheduleb_pdf, name='Scheduleb'),
    path('change_password/', views.change_password, name='change_my_password'),
    path('drivers/<int:customer_id>',
         permission_required('Procedure.list_drivers', 'Procedure:index')(views.list_drives)),
    path('add_driver/<int:customer_id>',
         permission_required('Procedure.add_drivers', 'Procedure:index')(views.add_driver)),
    path('edit_driver/<int:iddriver>',
         permission_required('Procedure.change_drivers', 'Procedure:index')(views.edit_driver)),
    path('change_status_driver/',
         permission_required('Procedure.change_status_driver', 'Procedure:index')(views.change_status_driver),
         name='cdriver'),
    path('datatable_driver/', login_required(DriversDatatable.as_view(), login_url='Procedure:login'), name='datatable_drivers'),
    path('add_exams/<int:iddriver>', permission_required('Procedure.add_exams', 'Procedure:index')(views.add_exams)),
    path('notes/<int:customer_id>', permission_required('Procedure.view_notes', 'Procedure:index')(views.list_notes)),
    path('add_notes/<int:customer_id>', login_required(views.CustomerNotesView.as_view(), login_url='Procedure:login')),
    path('projects/<int:customer_id>/<int:show_all>',
         permission_required('Procedure.view_projects', 'Procedure:index')(views.list_projects)),
    path('edit_projects/', permission_required('Procedure.change_projects', 'Procedure:index')(views.edit_projects)),
    path('edit_project/', permission_required('Procedure.change_projects', 'Procedure:index')(views.edit_project)),
    path('projects/<str:status>', views.show_projects),
    path('projects_add/', login_required(ProjectsView.as_view(action='Add'), login_url='Procedure:login'), name='Projects'),
    path('notes_projects/<int:idproject>/<int:is_chat>', views.notes_projects),
    path('edit_notes_projects/<int:idnote>', views.edit_notes_projects),
    path('projects_reports/', views_reports.projects_reports),
    path('summary_projects/<int:reload>', login_required(views.summary_projects, login_url='Procedure:login')),
    path('assign_project/', permission_required('Procedure.change_projects', 'Procedure:index')(views.assign_project), name='assign_project'),
    path('cards/<int:customer_id>', login_required(CardView.as_view(), 'Procedure:index')),
    path('add_cards/', permission_required('Procedure.add_cards', 'Procedure:index')(CardView.as_view())),
    path('edit_cards/', permission_required('Procedure.change_cards', 'Procedure:index')(CardView.as_view())),
    path('edit_cards/<int:card_id>/<str:field>/', permission_required('Procedure.change_cards', 'Procedure:index')(CardView.as_view())),
    path('status_cards/<int:card_id>/<str:field>/', permission_required('Procedure.delete_cards', 'Procedure:index')(CardView.as_view())),
    path('datatable_cards/', login_required(CardsDatatable.as_view(), 'Procedure:index')),
    path('applications/<int:customer_id>', views.list_applications),
    path('iftaapp/<int:customer_id>', pdf_views.iftaapp),
    path('iftalicenses/<int:customer_id>', pdf_views.ifta_licenses),
    path('iftacancel/<int:customer_id>', pdf_views.ifta_cancel),
    path('iftaremplace/<int:customer_id>', pdf_views.ifta_remplace),
    path('ifta_address_change_form/<int:customer_id>', pdf_views.ifta_address_change),
    path('ifta_fuel_taxes/<int:customer_id>', pdf_views.ifta_fuel_taxes),
    path('poalocal/<int:customer_id>', pdf_views.poa_local),
    path('billsale/<int:customer_id>', pdf_views.billsale_pdf),
    path('get_customertype/<int:customer_id>', pdf_views.get_typecustomer),
    path('transfers/<int:customer_id>', pdf_views.transfers_pdf),
    path('duplicate_title/<int:customer_id>', pdf_views.duplicate_title),
    path('personal_lease_agreement/<int:customer_id>', pdf_views.Personal_Lease_Agreement),
    path('surrender_license_plate/<int:customer_id>', pdf_views.Surrender_License_Plate),
    path('certificate_vessel_title/<int:customer_id>', pdf_views.certificate_vessel_title),
    path('certificate_mv_title/<int:customer_id>', pdf_views.certificate_mv_title),
    path('certificate_mh_title/<int:customer_id>', pdf_views.certificate_mh_title),
    path('get_unit/', pdf_views.data_unit),
    path('mcs150/<int:customer_id>', pdf_views.mcs150),
    path('clearing_house_account/<int:customer_id>', pdf_views.Clearing_House_Account.as_view()),
    path('irpapp/<int:customer_id>', pdf_views.irpapp),
    path('getCustomers/<int:customer_id>', pdf_views.getCustomers),
    path('irptransfers/<int:customer_id>', pdf_views.irp_transfers),
    path('irpnonuse/<int:customer_id>', pdf_views.irp_nonuse),
    path('irp_prepass/<int:customer_id>', pdf_views.irp_prepass),
    path('texasirp/<int:customer_id>', pdf_views.irp_texas),
    path('irp85100/<int:customer_id>', pdf_views.irp_85100),
    path('crttitle/<int:customer_id>', pdf_views.other_crttitle), # type: ignore
    path('license_plate/<int:customer_id>', login_required(pdf_views.license_plate, login_url='Procedure:login')),
    path('other_poa/<int:customer_id>', pdf_views.other_poa),
    path('other_keeping/<int:customer_id>', pdf_views.other_keeping),
    path('other_efile/<int:customer_id>', pdf_views.other_efile),
    path('other_lease/<int:customer_id>', pdf_views.other_lease),
    path('other_vin_verification/<int:customer_id>', pdf_views.other_vin_verification),
    path('other_general_affivadit/<int:customer_id>', pdf_views.other_general_affidavit),
    path('other_annual_vehicle_inspection/<int:customer_id>', pdf_views.other_annual_vehicle_inspection),
    path('other_florida_quit_claim_deed/<int:customer_id>', pdf_views.other_florida_quit_claim_deed), # type: ignore
    path('other_replacement_license_plate_validation_decal_parking_permit/<int:customer_id>', pdf_views.other_replacementLicensePlateValidationDecalParkingPermit),
    path('mcd356texas/<int:customer_id>', pdf_views.other_mcd356texas),
    path('permits_ny/<int:customer_id>', pdf_views.permits_ny),
    path('permits_nj/<int:customer_id>', pdf_views.permits_nj),
    path('permits_nm/<int:customer_id>', pdf_views.permits_nm),
    path('overweight_oversize/<int:customer_id>', pdf_views.permits_overweight_oversize),
    path('ifta_texas/<int:customer_id>', pdf_views.ifta_texas),
    path('daily_chart/', views_reports.daily_chart),
    path('invunpaid/', Invoice_Unpaid.as_view()),
    path('bills_paid/', views.bills_paid),
    path('credits/<int:show_all>', views.list_credits),
    path('paid_credit/', views.paid_credit),
    path('search_box/', views.search_box),
    path('consortium_pool/', views.random),
    path('newpool/', views.add_random),
    path('expirations/', views_reports.expirations),
    path('get_file/<str:name>', pdf_views.get_file),
    path('get_invoice/<int:idinvoice>', pdf_views.GeneratePDF.as_view()),
    path('edit_invoice/<int:idinvoice>', views.edit_invoice),
    path('upload_receipts/<int:idcustomer>', views.upload_receipts_fuel_taxes, name='upload_receipts'),
    path('get_excel_template/<str:name>', views.get_file),
    path('export_summary/', views_reports.print_summary),
    path('detail_project/<int:project_id>', login_required(views.details_project, login_url='Procedure:login'), name='detail_project'),
    path('get_state_zipcode/', views.get_state_zipcode),
    path('bill_sale_interstate/<int:customer_id>', pdf_views.BillSaleInterstate.as_view()),
    path('small-corp/<int:customer_id>', pdf_views.small_corp),
    path('update_dot/', views.update_dot),
    path('category_road_tax/', views.category_road_tax),
    path('category_road_tax/<int:id>', views.category_road_tax),
    path('florida_tag_gvw/', views.florida_tag_classification),
    path('florida_tag_gvw/<int:id>', views.florida_tag_classification),
    path('sellers/', login_required(Sellers.as_view(), login_url='Procedure:login'), name='sellers'),
    path('datatable_sales_details/', login_required(SalesDetails.as_view(), login_url='Procedure:login'), name='sellers'),
    path('update_projects_invoice/', views.update_idinvoice),
    path('customer_files/<int:idcustomer>', login_required(views.CustomerFilesView.as_view(), login_url='Procedure:login')),
    path('datatable_files/', login_required(CustomerFilesTable.as_view(), login_url='Procedure:login')),
    path('upload_files/<int:customer_id>', login_required(views.CustomerFilesView.as_view(), login_url='Procedure:login')),
    path('delete_files_customer/<int:id>', login_required(views.CustomerFilesView.as_view(), login_url='Procedure:login')),
    path('cover/<int:idcustomer>', login_required(docx_view.generate_cover, login_url='Procedure:login')),
    path('certificate_random_test/<int:customer_id>', login_required(Certificate_random_test.as_view(), login_url='Procedure:login')),
    path('certificate_enrollment_alcohol_drug/<int:customer_id>', login_required(Certificate_Enrollment_Alcohol_Drug.as_view(), login_url='Procedure:login')),
    path('certificate_alcohol_drug/<int:customer_id>', login_required(Certificate_Alcohol_Drugs.as_view(), login_url='Procedure:login')),
    path('certificate_alcohol/<int:customer_id>', login_required(Certificate_Alcohol.as_view(), login_url='Procedure:login')),
    path('labcorp/<int:customer_id>', login_required(pdf_views.labcorp, login_url='Procedure:login')),
    path('separate_odometer/<int:customer_id>', login_required(pdf_views.separate_odometer, login_url='Procedure:login')),
    path('application_transporter_license_plate/<int:customer_id>', login_required(pdf_views.application_transporter_license_plate, login_url='Procedure:login')),
    path('news/', login_required(views.NewsView.as_view(), login_url='Procedure:login')),
    path('datatable_news/', login_required(NewsTable.as_view(), login_url='Procedure:login'), name='datatable_news'),
    path('send_email_invoice/<int:invoice_id>', login_required(Send_invoice_email.as_view(), login_url='Procedure:login'), name='sendemail'),
    path('do_fuel_taxes/<int:customer_id>', login_required(views.do_fuel_taxes, login_url='Procedure:login'), name='do_fuel_taxes'),
    path('sent_emails/<int:invoice_id>', login_required(Sent_Emails.as_view(), login_url='Procedure:login'), name='sent_emails'),
    path('tasks/', include('Direct.Apps.Procedure.routes.tasks')),
    path('alert_notifications/', login_required(views.alertNotifications, login_url='Procedure:login'), name='alert_notifications' ),
    path('updatedot/', login_required(UpdateDot.as_view(), login_url='Procedure:login'), name='updatedot'),
    path('services/', login_required(ServicesView.as_view(), login_url='Procedure:login'), name='services'),
    path('datatable_services/', login_required(ServicesTable.as_view(), login_url='Procedure:login'), name='datatable_services'),
    #path('add_note/', views.add_note)
    #path('upgrade_customers/', views.update_idinvoice)
    #path('upgrade_card', views.upgrade_cards)
    path('certificate_random_test_email/<int:customer_id>', login_required(SendCertificateRandomTestEmail.as_view(), login_url='Procedure:login'), name='send_certificate_randomtest'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
