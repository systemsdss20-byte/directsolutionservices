import base64
import os
import shutil

import pypdftk
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from django_xhtml2pdf.utils import render_to_pdf_response
from datetime import date, datetime

from xhtml2pdf import pisa
from ..helpers.message import MessageResponse
from .models import Recive, Customers, Millages, Invoices, Invoice_det, Invoice_paid, Units, States, User, Drivers
from django.conf import settings


@login_required(login_url='Procedure:login')
def view_invoice(request, idinvoice):
    invoice = Invoices()
    customer = Customers()
    Paid = {"datepaid": '', "total_paid": '0', "check": '0', "cash": '0',
            "credit_card": '0', "zelle": '0'}
    msg = ''
    try:
        details_invoice = Invoice_det.objects.select_related("idinvoice__idcustomer").filter(idinvoice=idinvoice) \
            .only("idinvoice", "code", "service", "quantity", "rate", "discount", "amount", "coments", "idinvoice",
                  "discountype",
                  "idinvoice__invdate", "idinvoice__amount", "idinvoice__idcustomer", "idinvoice__status", "idinvoice__deu",
                  "idinvoice__idcustomer__cusname", "idinvoice__idcustomer__address", "idinvoice__idcustomer__city",
                  "idinvoice__idcustomer__state", "idinvoice__idcustomer__codepostal", "idinvoice__idcustomer__mobile1"
                  )
        invoice = details_invoice.first().idinvoice
        invoice.invdate = invoice.invdate.strftime("%m/%d/%Y")
        customer = invoice.idcustomer
        total_paid = Invoice_paid.objects.filter(idinvoice=idinvoice).aggregate(total=Sum("paid"))
        check = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Check").aggregate(check=Sum("paid"))
        cash = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Cash").aggregate(cash=Sum("paid"))
        credit_card = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Credit Card").aggregate(
            credit_card=Sum("paid"))
        zelle = Invoice_paid.objects.filter(idinvoice=idinvoice, typepaid="Zelle").aggregate(zelle=Sum('paid'))
        datepaid = Invoice_paid.objects.only("datepaid").filter(idinvoice=idinvoice).latest('datepaid')
        datepaid = datepaid.datepaid.strftime('%m/%d/%Y')
        Paid = {"datepaid": datepaid, "total_paid": total_paid["total"], "check": check["check"], "cash": cash["cash"],
                "credit_card": credit_card["credit_card"], "zelle": zelle["zelle"]}
    except Exception as e:
        print(e)
    if invoice.invdate is None:
        invoice = Invoices.objects.get(pk=idinvoice)
        invoice.invdate = invoice.invdate.strftime("%m/%d/%Y")
        customer = invoice.idcustomer
        msg = 'There are no invoices details'
    return render(request, "PDF/pdfInvoice.html", {"details": details_invoice, "invoice": invoice, "customer": customer, "customer_id": invoice.idcustomer_id, "Paid": Paid, 'message': msg})


@login_required(login_url='Procedure:login')
def pdf_recive(request):
    idcustomer = request.POST.get("idcustomer")
    idunit = request.POST.get("idunit")
    year = request.POST.get("year")
    quarter = request.POST.get("quarter")
    customer = Customers.objects.only('idcustomer', 'cusname').get(idcustomer=idcustomer)
    context = {}
    try:
        if "1" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=1, date__month__lte=3)
            first_month = report.filter(date__month=1)
            second_month = report.filter(date__month=2)
            third_month = report.filter(date__month=3)
            first_title = "JANUARY"
            second_title = "FEBRUARY"
            third_title = "MARCH"
            first_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=1).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            second_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month=2).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            third_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=3).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
        if "2" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=4,
                                                 date__month__lte=6)
            first_month = report.filter(date__month=4)
            second_month = report.filter(date__month=5)
            third_month = report.filter(date__month=6)
            first_title = "APRIL"
            second_title = "MAY"
            third_title = "JUNE"
            first_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=4).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            second_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                         date__month=5).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            third_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=6).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
        if "3" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=7,
                                                 date__month__lte=9)
            first_month = report.filter(date__month=7)
            second_month = report.filter(date__month=8)
            third_month = report.filter(date__month=9)
            first_title = "JULY"
            second_title = "AUGUST"
            third_title = "SEPTEMBER"
            first_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=7).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            second_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                         date__month=8).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            third_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=9).values(
                "state").annotate(mile=Sum("miles")).annotate(gallon=Sum("gallons"))
        if "4" == quarter:
            report = Recive.objects.all().filter(idcustomer=idcustomer, idunit=idunit, year=year, date__month__gte=10,
                                                 date__month__lte=12)
            first_month = report.filter(date__month=10)
            second_month = report.filter(date__month=11)
            third_month = report.filter(date__month=12)
            first_title = "OCTOBER"
            second_title = "NOVEMBER"
            third_title = "DECEMBER"
            first_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=10).values("state").annotate(
                mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            second_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                         date__month=11).values("state").annotate(
                mile=Sum("miles")).annotate(gallon=Sum("gallons"))
            third_month_summary = Recive.objects.filter(idcustomer=idcustomer, idunit=idunit, year=year,
                                                        date__month=12).values("state").annotate(
                mile=Sum("miles")).annotate(gallon=Sum("gallons"))
        cusname = '%s - %s' % (customer.idcustomer, customer.cusname)
        user_login = request.user
        createby = user_login.first_name + " " + user_login.last_name
        context = {
            "customer": cusname, "unit": idunit, "year": year, "createby": createby,
            "first_title": first_title, "second_title": second_title, "third_title": third_title,
            "first_month": first_month, "second_month": second_month, "third_month": third_month,
            "first_month_summary": first_month_summary, "second_month_summary": second_month_summary,
            "third_month_summary": third_month_summary
        }
    except Exception as e:
        print(e)
    pdf = render_to_pdf_response('PDF/pdf_recive.html', context, "recive.pdf")
    return HttpResponse(pdf, content_type='application/pdf')


@login_required(login_url='Procedure:login')
def cover_pdf(request, customer_id):
    if request.method == "POST":
        try:
            cusname = str(request.POST.get("cusname"))
            year = int(request.POST.get("year"))
            quarter = int(request.POST.get("quarter"))
            list_quarter = {
                1: "1St Quarter(Jan-Mar)",
                2: "2Nd Quarter(Apr-Jun)",
                3: "3Rd Quarter(Jul-Sep)",
                4: "4Th Quarter(Oct-Dec)"
            }
            if request.POST.get("iftaid") is not None:
                iftaid = request.POST.get("iftaid")
            else:
                iftaid = " "
            today = date.today().strftime("%m-%d-%Y")
            iftatotal = float(request.POST.get("iftatotal"))
            penalty = float(request.POST.get("penalty"))
            kentucky = float(request.POST.get("kentucky"))
            new_mexico = float(request.POST.get("new_mexico"))
            new_york = float(request.POST.get("new_york"))
            try:
                millage = Millages.objects.only('total', 'ky', 'nm', 'ny').get(idcustomer=customer_id, year=year,
                                                                               qtr=quarter)
            except Exception as exc:
                print(exc)
                message = "There are not data in %s" % str(list_quarter.get(quarter))
                response = JsonResponse({"message": message, "type": "error"})
                return HttpResponse(response, content_type="application/json", status=500)
            data = {
                'CUSTOMER': cusname, 'QUARTER': list_quarter.get(quarter), 'IFTA': iftaid, 'DATE': today,
                'IFTATOTAL': iftatotal,
                'PENALTY': penalty, 'KYU': kentucky, 'NM': new_mexico, 'NY': new_york, 'MILES': millage.total,
                'MILESKYU': millage.ky, 'MILESNM': millage.nm, 'MILESNY': millage.ny
            }
            path_template = settings.TEMPLATES_PDF + '/COVER.pdf'
            template = FileSystemStorage(location=path_template)
            out_file = settings.FILES_PDF + '/cover%s.pdf' % customer_id
            filepdf = pypdftk.fill_form(template.location, data, out_file, flatten=False)
            # out_pdf = pypdftk.concat([generate_pdf], FileSystemStorage(location='FilePDF/filled.pdf'))
            tmp = open(filepdf, "rb").read()
            encoded = base64.b64encode(tmp)
            os.remove(filepdf)
            return HttpResponse(encoded, content_type='application/pdf')
        except FileNotFoundError as error:
            print(error)


@login_required(login_url='Procedure:login')
def scheduleb_pdf(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        idmillage = request.POST.get("idmillage")
        query = "SELECT Sum(`fl`), Sum(`al`), Sum(`ak`), Sum(`ar`), Sum(`az`), Sum(`ca`), Sum(`co`), Sum(`ct`), Sum(`dc`), Sum(`de`), " \
                "Sum(`ga`), Sum(`ia`), Sum(`id`), Sum(`il`), Sum(`in1`), Sum(`ks`), Sum(`ky`), Sum(`la`), Sum(`ma`), Sum(`md`), Sum(`me`), " \
                "Sum(`mi`), Sum(`mn`), Sum(`mo`), Sum(`ms`), Sum(`mt`), Sum(`nc`), Sum(`nd`), Sum(`ne`), Sum(`nh`), Sum(`nj`),Sum(`nm`), " \
                "Sum(`nv`), Sum(`ny`), Sum(`oh`), Sum(`ok`), Sum(`or1`), Sum(`pa`), Sum(`ri`), Sum(`sc`), Sum(`sd`), Sum(`tn`), Sum(`tx`), " \
                "Sum(`ut`), Sum(`va`), Sum(`vt`), Sum(`wa`),Sum(`wi`), Sum(`wv`), Sum(`wy`), Sum(`ab`), Sum(`bc`), Sum(`mb`), Sum(`mx`), " \
                "Sum(`nb`), Sum(`nl`), Sum(`ns`), Sum(`nt`), Sum(`on1`), Sum(`pe`), Sum(`qc`), Sum(`sk`), Sum(`yt`), Sum(`total`)" \
                " FROM millages WHERE idcustomer = %s and idmillage IN (%s)" % (customer_id, idmillage)
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except Exception as e:
                print(e)
                message = "There are not data"
                response = JsonResponse({"message": message, "type": "error"})
                return HttpResponse(response, content_type="application/json", status=500)
        path_template = settings.TEMPLATES_PDF + '/SCHEDULEB.pdf'
        template = FileSystemStorage(location=path_template)
        # out_file = settings.FILES_PDF + '\\scheduleb%s.pdf' % customer_id
        out_file = settings.FILES_PDF + '/scheduleb%s.pdf' % customer_id
        data = {
            'FL': row[0], 'AL': row[1], 'AK': row[2], 'AR': row[3], 'AZ': row[4], 'CA': row[5], 'CO': row[6],
            'CT': row[7], 'DC': row[8], 'DE': row[9], 'GA': row[10], 'IA': row[11], 'ID': row[12], 'IL': row[13],
            'IN': row[14], 'KS': row[15], 'KY': row[16], 'LA': row[17], 'MA': row[18], 'MD': row[19], 'ME': row[20],
            'MI': row[21], 'MN': row[22], 'MO': row[23], 'MS': row[24], 'MT': row[25], 'NC': row[26], 'ND': row[27],
            'NE': row[28], 'NH': row[29], 'NJ': row[30], 'NM': row[31], 'NV': row[32], 'NY': row[33], 'OH': row[34],
            'OK': row[35], 'OR': row[36], 'PA': row[37], 'RI': row[38], 'SC': row[39], 'SD': row[40], 'TN': row[41],
            'TX': row[42], 'UT': row[43], 'VA': row[44], 'VT': row[45], 'WA': row[46], 'WI': row[47], 'WV': row[48],
            'WY': row[49], 'AB': row[50], 'BC': row[51], 'MB': row[52], 'MX': row[53], 'NB': row[54], 'NL': row[55],
            'NS': row[56], 'NT': row[57], 'ON': row[58], 'PE': row[59], 'QC': row[60], 'SK': row[61], 'YT': row[62],
            'TOTAL': row[63]
        }
        filepdf = pypdftk.fill_form(template.location, data, out_file, flatten=False)
        tmp = open(filepdf, "rb").read()
        encoded = base64.b64encode(tmp)
        os.remove(filepdf)
        return HttpResponse(encoded, content_type='application/pdf')


@login_required(login_url='Procedure:login')
def iftaapp(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        #agents = User.objects.all().filter(is_active=True, is_superuser=False).only('id', 'first_name', 'last_name')
        return render(request, 'Procedure/Customers/Applications/IFTA/iftaapp.html',
                      {'customer': customer})
    if request.method == 'POST':
        apptype = int(request.POST.get('apptype'))
        account = int(request.POST.get('account'))
        #agents = request.POST.get('agents')
        qtyplate = request.POST.get('qtyplate')
        plates = request.POST.getlist('plate')
        customer = Customers.objects.get(idcustomer=customer_id)
        state = States.objects.only('state', 'codestate').get(codestate=customer.state)
        date = datetime.now()
        date = datetime(date.year, date.month, date.day).strftime('%m/%d/%Y')
        data = {
                'FEIN EMPLOYER': customer.fein,
                'FEIN': customer.fein,
                'BUSINESS ADDRESS': customer.address, 'CITY': customer.city,
                #'AUTHORIZED AGENT NAME': agents,
                'STATE': state.codestate,
                'ZIP CODE': customer.codepostal if customer.codepostal else '',
                'COUNTY': customer.county if customer.county else '',
                'DOT': customer.dotid if customer.dotid else '',
                'IRP ACCOUNT': customer.irpid if customer.irpid else '',
                'CONTACT PERSON': customer.contact1,
                'CONTACT EMAIL': customer.email if customer.email else '',
                'CONTACT PHONE': customer.mobile1 if customer.mobile1 else '',
                'TELEPHONE': customer.mobile1 if customer.mobile1 else '',
                'TELEPHONE  REQUIRED': customer.mobile1 if customer.mobile1 else '',
                'DATE': date, 'NAME': customer.owner + ' ' + customer.owner_surname, 'PRINTED NAME': customer.owner + ' ' + customer.owner_surname,
                'FL DRIVER LICENSE': customer.lic if customer.lic else '',
                'HOME ADDRESS': customer.address,
        }
        if account == 1:
            data['ACCOUNT'] = 'COMPANY'
        if account == 2:
            data['BUSINESS NAME'] = customer.owner + ' ' + customer.owner_surname
            data['ACCOUNT'] = 'PERSONAL'
            data['TITLE'] = 'OWNER'
            data['TITLE_3'] = 'OWNER'
        else:
            data['BUSINESS NAME'] = customer.cusname
            if customer.corptype == 'INC' or customer.corptype == 'CORP':
                data['TITLE'] = 'PRESIDENT'
                data['TITLE_3'] = 'PRESIDENT'
            elif customer.corptype == 'LLC':
                data['TITLE'] = 'AMBR'
                data['TITLE_3'] = 'AMBR'
            else:
                data['TITLE'] = '?'
                data['TITLE_3'] = '?'

        if apptype == 1:
            #data['Application Type'] = 'NEW ACCOUNT'
            template_path = 'IFTA/85008.pdf'
        if apptype == 2:
            data['TYPE APP'] = 'RENEWAL'
            template_path = 'IFTA/IFTANEWORRENEW.pdf'
            #data['Decal Year'] = datetime.today().year
            data['Decal Year'] = 2026
            data['Print Name'] = customer.owner + " " + customer.owner_surname
        if apptype == 3:
            data['TYPE APP'] = 'ADDITIONAL'
            template_path = 'IFTA/IFTANEWORRENEW.pdf'
            #data['Decal Year'] = datetime.today().year
            data['Decal Year'] = 2026
            data['Print Name'] = customer.owner + " " + customer.owner_surname
        count = int(qtyplate)
        data['Number of Vehicles'] = count
        data['Total'] = count * 4
        while count != 0:
            count = count - 1
            frmplate = "PLATE%s" % count
            data[frmplate] = plates[count]

        file_name = 'iftaapp%s.pdf' % customer_id
        generate_pdf_fill(template_path, data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_licenses(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/IFTA/ifta_licenses.html',
                      {'customer': customer})
    if request.method == 'POST':
        issuedate = request.POST.get('issuedate')
        customer = Customers.objects.get(idcustomer=customer_id)
        year = date.today().year
        dateinitial = '01/01/{0}'.format(year)
        dateinitial = datetime.strptime(dateinitial, '%m/%d/%Y').date()
        datefinal = '12/31/{0}'.format(year)
        datefinal = datetime.strptime(datefinal, '%m/%d/%Y').date()
        issuedate = datetime.strptime(issuedate, '%m/%d/%Y').date()
        if issuedate >= dateinitial:
            effdate = issuedate
        else:
            effdate = dateinitial
        data = {'NAME': customer.cusname, 'IFTA': customer.iftaid, 'ISSUEDATE': issuedate.strftime('%m/%d/%Y'),
                'EFFDATE': effdate.strftime('%m/%d/%Y'), 'EXPDATE': datefinal.strftime('%m/%d/%Y')}
        file_name = 'iftalicense{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/LICENSE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_texas(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('owner', 'owner_surname', 'city', 'codepostal', 'county', 'ssn', 'fein').get(idcustomer=customer_id)
        state_c = States.objects.only('codestate').get(codestate=customer.state) if customer.state else ''
        data = {'1_name': customer.owner + ' ' + customer.owner_surname, '2_city': customer.city if customer.city else '', '2_address': customer.address,
                '2_zip': customer.codepostal if customer.codepostal else '', '2_state': state_c,
                '2_county': customer.county if customer.county else '', '4_fei': customer.fein if customer.fein else '',
                '5_ss': customer.ssn if customer.ssn else ''
                }
        file_name = 'ap178_{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/ap178.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_fuel_taxes(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('owner', 'owner_surname', 'cusname').get(idcustomer=customer_id)
        data = {
            'OWNER': '{0} {1}'.format(customer.owner, customer.owner_surname),
            'CUSTOMER ID': customer_id,
            'COMPANY': customer.cusname
        }
        file_name = 'fuel_taxes_form_{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/FUEL_TAXES_FORM.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_cancel(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/IFTA/ifta_cancel.html',
                      {'customer': customer})
    if request.method == 'POST':
        cancel_date = request.POST.get('canceldate')
        cancel_date = datetime.strptime(cancel_date, '%m/%d/%Y')
        customer = Customers.objects.get(idcustomer=customer_id)
        today = date.today().strftime("%m/%d/%Y")
        data = {'DATE': today, 'IFTA': customer.iftaid, 'CUSTOMER': customer.cusname,
                'CANCELDATE': cancel_date.strftime('%m/%d/%Y'), 'day': cancel_date.day,
                'month': cancel_date.month, 'year': cancel_date.year,
                'OWNER': customer.owner + ' ' + customer.owner_surname
                }
        file_name = 'ifta_cancel_licenses{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/IFTACANCELATION.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_remplace(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/IFTA/ifta_remplace.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        today = date.today().strftime("%m/%d/%Y")
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'iftaid').get(idcustomer=customer_id)
        unit = Units.objects.only('type', 'year', 'make', 'vin', 'irp').get(idunit=idunit)
        data = {'Date': today, 'IFTA': customer.iftaid, 'CUSTOMER': customer.cusname, 'TYPE': unit.type,
                'YEAR': unit.year, 'MAKE': unit.make,
                'VIN': unit.vin, 'PLATE': unit.irp, 'OWNER': customer.owner + ' ' + customer.owner_surname}
        file_name = 'ifta_remplace{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/IFTAREMPLACE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def ifta_address_change(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/IFTA/change_address.html', {'customer': customer})
    if request.method == 'POST':
        date = request.POST.get('date')
        account = int(request.POST.get('account'))
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'iftaid').get(idcustomer=customer_id)
        data = {
            'IRP Account': customer.irpid if customer.irpid else '',
            'IFTA Account': customer.iftaid if customer.iftaid else '',
            'Email': customer.email if customer.email else '',
            'Telephone': customer.mobile1 if customer.mobile1 else '',
            'Date': date, 'Print Name': customer.owner + ' ' + customer.owner_surname
        }
        if account == 1:
            data['Name'] = customer.cusname
        else:
            data['Name'] = customer.owner + " " + customer.owner_surname
        file_name = 'ifta_address{0}.pdf'.format(customer_id)
        generate_pdf_fill('IFTA/IFTAADDRESSCHANGE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


def poa_local(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        agents = User.objects.all().filter(is_active=True, is_superuser=False).only("id", "first_name", "last_name")
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/LOCAL/poalocal.html',
                      {'customer': customer, 'units': units, 'agents': agents})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        agent = request.POST.get('agents')
        owner = request.POST.get('owner')
        co_owner = request.POST.get('co_owner')
        today = date.today()
        unit = Units.objects.only('idunit', 'type', 'year', 'make', 'vin', 'title', 'idcustomer__cusname',
                                  'idcustomer__owner', 'idcustomer__owner_surname', 'idcustomer__ssn',
                                  'idcustomer__fein', 'idcustomer__lic', 'idcustomer__explic', 'idcustomer__address',
                                  "idcustomer__city", 'idcustomer__state', 'idcustomer__codepostal').get(idunit=idunit)
        # VEHICLE
        data = {'Month': today.month, 'Day': today.day, 'Year': today.year, 'AGENT': agent.upper(), 'TYPE 1': unit.type, 'YEAR 1': unit.year, 'MAKE 1': unit.make,
                'VIN 1': unit.vin, 'TITLE 1': unit.title}
        # OWNERS
        if owner == '2':
            data['OWNER'] = unit.idcustomer.owner + ' ' + unit.idcustomer.owner_surname
            data['IDEN-OWNER'] = unit.idcustomer.lic
            if unit.idcustomer.explic == '0001/01/01':
                data['DOB-OWNER'] = ' '
            else:
                data['DOB-OWNER'] = unit.idcustomer.explic.strftime('%m/%d/%Y')
            data['ADDRESS-OWNER'] = unit.idcustomer.address
            data['CITY-OWNER'] = unit.idcustomer.city
            if unit.idcustomer.state:
                data['STATE-OWNER'] = unit.idcustomer.state[:2]
            data['ZIP-OWNER'] = unit.idcustomer.codepostal
        if co_owner == '2':
            data['CO-OWNER'] = unit.idcustomer.owner + ' ' + unit.idcustomer.owner_surname
            data['IDEN-CO-OWNER'] = unit.idcustomer.lic
            if unit.idcustomer.explic == '0001/01/01':
                data['DOB-CO-OWNER'] = ' '
            else:
                data['DOB-CO-OWNER'] = unit.idcustomer.explic.strftime('%m/%d/%Y')
            data['ADDRESS-CO-OWNER'] = unit.idcustomer.address
            data['CITY-CO-OWNER'] = unit.idcustomer.city
            data['STATE-CO-OWNER'] = unit.idcustomer.state[:2]
            data['ZIP-CO-OWNER'] = unit.idcustomer.codepostal
        if co_owner == '1':
            data['CO-OWNER'] = unit.idcustomer.cusname
            data['IDEN-CO-OWNER'] = unit.idcustomer.fein
            data['ADDRESS-CO-OWNER'] = unit.idcustomer.address
            data['CITY-CO-OWNER'] = unit.idcustomer.city
            data['STATE-CO-OWNER'] = unit.idcustomer.state[:2] if unit.idcustomer.state else ''
            data['ZIP-CO-OWNER'] = unit.idcustomer.codepostal
        # Generate pdf
        file_name = 'poa_local{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/POALOCAL.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def billsale_pdf(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        result = {'customer': customer, 'units': units}
        return render(request, 'Procedure/Customers/Applications/LOCAL/billsalelocal.html', result)
    if request.method == 'POST' :
        idunit = int(request.POST.get('unit'))
        unit = Units.objects.only('year', 'make', 'type', 'vin', 'title', 'color', 'price').get(pk=idunit,
                                                                                                idcustomer=customer_id)
        data = {'YEAR': unit.year, 'MAKE': unit.make, 'TYPE': unit.type, 'VIN': unit.vin, 'TITLE': unit.title,
                'COLOR': unit.color, 'PRICE': unit.price,
                'S-NAME': request.POST.get('name_seller'), 'S-ADDRESS': request.POST.get('address_seller'),
                'S-CITY': request.POST.get('city_seller'), 'S-STATE': request.POST.get('state_seller'),
                'S-ZIP': request.POST.get('zipcode_seller'), 'S-DATE': request.POST.get('date_seller'),
                'P-NAME': request.POST.get('name_purchaser'), 'P-ADDRESS': request.POST.get('address_purchaser'),
                'P-CITY': request.POST.get('city_purchaser'), 'P-STATE': request.POST.get('state_purchaser'),
                'P-ZIP': request.POST.get('zipcode_purchaser'), 'P-DATE': request.POST.get('date_seller')
                }
        file_name = 'billsale{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/BILLSALE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def get_typecustomer(request, customer_id):
    if request.method == 'GET' :
        type = request.GET.get('type')
        if type == '1':
            customer = Customers.objects.only('cusname', 'address', 'city', 'state', 'codepostal', 'fein').get(
                pk=customer_id)
            json_customer = {'cusname': customer.cusname, 'address': customer.address, 'city': customer.city,
                             'state': customer.state, 'codepostal': customer.codepostal, 'fein': customer.fein}
        if type == '2':
            customer = Customers.objects.only('owner', 'owner_surname', 'address', 'city', 'state', 'codepostal', 'lic').get(
                pk=customer_id)
            json_customer = {'owner': customer.owner + ' ' + customer.owner_surname, 'address': customer.address, 'city': customer.city,
                             'state': customer.state, 'codepostal': customer.codepostal, 'lic': customer.lic}
        return JsonResponse(json_customer)


@login_required(login_url='Procedure:login')
def transfers_pdf(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        result = {'customer': customer, 'units': units}
        return render(request, 'Procedure/Customers/Applications/LOCAL/transferslocal.html', result)
    if request.method == 'POST' :
        vehicle_type = int(request.POST.get('vehicle_type'))
        data = {}
        if vehicle_type == 1:
            data['mv'] = 'Yes'
        if vehicle_type == 2:
            data['mh'] = 'Yes'
        if vehicle_type == 3:
            data['ves'] = 'Yes'
        # Owner
        data['owner name'] = str(request.POST.get('name_owner'))
        data['FL DL/FEID#'] = str(request.POST.get('feinolic_owner'))
        data['owner mailing add'] = str(request.POST.get('address_owner'))
        data['city'] = str(request.POST.get('city_owner'))
        data['st'] = str(request.POST.get('state_owner'))
        data['zip'] = str(request.POST.get('zipcode_owner'))
        data['date10'] = str(request.POST.get('date_transfers'))
        # CO-OWNER
        if int(request.POST.get('type_coowner')) != 0:
            data['co-owner name'] = str(request.POST.get('name_coowner'))
            data['FL DL/FEID#2'] = str(request.POST.get('feinolic_coowner'))
            data['co-owner mailing add'] = str(request.POST.get('address_coowner'))
            data['city2'] = str(request.POST.get('city_coowner'))
            data['st2'] = str(request.POST.get('state_coowner'))
            data['zip2'] = str(request.POST.get('zipcode_coowner'))
            data['date102'] = str(request.POST.get('date_transfers'))
        # VEHICLE
        data['VIN'] = str(request.POST.get('vin'))
        data['VIN3'] = str(request.POST.get('vin'))
        data['make'] = str(request.POST.get('make'))
        data['MV-MH-Ves-year'] = str(request.POST.get('year'))
        data['body'] = str(request.POST.get('type_unit'))
        data['color'] = str(request.POST.get('color'))
        data['FL title number 1'] = str(request.POST.get('title'))
        file_name = 'transfers{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/TRANSFERS.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def duplicate_title(request, customer_id):

    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/duplicate_title.html',
                      {'customer': customer, 'units': units})

    if request.method == 'POST':
        selected_owner = request.POST.get('owner')
        today = date.today().strftime("%m/%d/%Y")
        vessel_duplicate = request.POST.get('vessel_duplicate')
        type_application = request.POST.get('type_application')
        customer = Customers.objects.get(idcustomer=customer_id)
        unit = Units.objects.get(idunit=request.POST.get('unit'))
        # OWNERS
        owner_name = customer.owner + ' ' + customer.owner_surname
        data = {
            'OWNERS NAME': customer.cusname if selected_owner == '1' and selected_owner != '' else owner_name,
            'Owners EMail Address': customer.email, 'OWNERS MAILING ADDRESS': customer.address, 'CITY': customer.city,
            'STATE': customer.state, 'ZIP': customer.codepostal, 'printed seller owner lienholder': owner_name,
            'owner check mark': 'yes', type_application: 'yes', vessel_duplicate: 'yes', 'LIENHOLDER DATE OF LIEN': today,
            'VehicleVessel Identification Number': unit.vin if unit.vin is not None else '', 'MakeManufacturer': unit.make if unit.make is not None else '',
            'Year': unit.year if unit.year is not None else '', 'Color': unit.color if unit.color is not None else '',
            'License Plate or Vessel Registration Number': unit.irp if unit.irp is not None else '',
            'Florida Title Number': unit.title if unit.title is not None else '', 'Body': unit.type if unit.type is not None else ''
        }
        # Generate pdf
        file_name = 'duplicate_title{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/DUPLICATE_TITLE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def Personal_Lease_Agreement(request, customer_id):

    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/personal_lease_agreement.html',
                      {'customer': customer, 'units': units})

    if request.method == 'POST':
        selected_owner = request.POST.get('owner')
        today = date.today().strftime("%m/%d/%Y")
        customer = Customers.objects.get(idcustomer=customer_id)
        unit = Units.objects.get(idunit=request.POST.get('unit'))
        # OWNERS
        owner_name = customer.owner + ' ' + customer.owner_surname
        data = {
            'NAME': customer.cusname if selected_owner == '1' and selected_owner != '' else owner_name,
            'ADDRESS 2': customer.address, 'CITY': customer.city + ', ' + customer.state + ' ' + customer.codepostal,
            'CONTACT': customer.contact1, 'PHONE': customer.mobile1, 'FEIN': customer.fein,
            'VIN': unit.vin if unit.vin is not None else '', 'MAKE': unit.make if unit.make is not None else '',
            'YEAR': unit.year if unit.year is not None else '', 'UNIT': unit.nounit if unit.nounit is not None else ''
        }
        # Generate pdf
        file_name = 'duplicate_title{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/LEASE_AGREEMENT.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def Surrender_License_Plate(request, customer_id):

    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        today = date.today().strftime("%m/%d/%Y")
        return render(request, 'Procedure/Customers/Applications/LOCAL/surrender_license_plate.html',
                      {'customer': customer, 'units': units, 'today': today})


    if request.method == 'POST':
        selected_owner = request.POST.get('owner')
        selected_date = request.POST.get('date')
        selected_plate = request.POST.get('plate')
        customer = Customers.objects.get(idcustomer=customer_id)
        # OWNERS
        owner_name = customer.owner + ' ' + customer.owner_surname
        data = {
            'Date': selected_date,
            'License Plate Numbers': selected_plate,
            'Owner Name': customer.cusname if selected_owner == '1' and selected_owner != '' else owner_name
        }
        # Generate pdf
        file_name = 'duplicate_title{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/Surrender-License-Plate-Form.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def certificate_vessel_title(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/certificate_title.html',
            {
                'customer': customer, 'units': units,
                'certificate_title': 'CERTIFICATE OF VESSEL TITLE',
                'url': 'certificate_vessel_title'
            }
        )

    if request.method == 'POST':
        customer = Customers.objects.only('owner', 'owner_surname', 'cusname').get(idcustomer=customer_id)
        selected_owner = request.POST.get('owner')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.get(idunit=request.POST.get('unit'))
        data = {
            'Owners Name': customer.cusname if selected_owner == '1' and selected_owner != '' else '{0} {1}'.format(customer.owner, customer.owner_surname),
            'Full Name':'{0} {1}'.format(customer.owner, customer.owner_surname),
            'Owners Phone Number': customer.mobile1, 'Owner Date of Birth': customer.explic.strftime('%m/%d/%Y'),
            'Owners Mailing Address': customer.address, 'Owners City': customer.city,
            'Owners State': customer.state, 'Owners Zip Code': customer.codepostal,
            'Owners Residential Street Address': customer.address, 'Owners Residential City': customer.city,
            'Owners Residential State': customer.state, 'Owners Residential Zip Code': customer.codepostal,
            'Owners Email': customer.email, 'FL/DO Number': customer.dotid, 'Date': today, 'VIN': unit.vin,
            'TITLE': unit.title, 'MAKE': unit.make, 'Year': unit.year, 'Weight': unit.empty,
            'DL/FEI': customer.fein if selected_owner == '1' and selected_owner != '' else customer.lic
        }
        file_name = '82040_vs_{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/82040-vs.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def certificate_mv_title(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/certificate_title.html',
            {
                'customer': customer, 'units': units,
                'certificate_title': 'CERTIFICATE OF MOBILE VEHICLE TITLE',
                'url': 'certificate_mv_title'
             }
        )
    if request.method == 'POST':
        customer = Customers.objects.only('owner', 'owner_surname', 'cusname').get(idcustomer=customer_id)
        selected_owner = request.POST.get('owner')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.get(idunit=request.POST.get('unit'))
        data = {
            'Owners': customer.cusname if selected_owner == '1' and selected_owner != '' else '{0} {1}'.format(
                customer.owner, customer.owner_surname),
            'Owners Name': '%s %s' % (customer.owner, customer.owner_surname),
            'Full Name': '{0} {1}'.format(customer.owner, customer.owner_surname),
            'Owners Phone Number': customer.mobile1, 'Owners Date of Birth': customer.explic.strftime('%m/%d/%Y'),
            'Owners Mailing Address': customer.address, 'Owners Mailing City': customer.city,
            'Owners Mailing State': customer.state, 'Owners Zip Code': customer.codepostal,
            'Owners Residential Street Address': customer.address, 'Owners Residential City': customer.city,
            'Owners Residential State': customer.state, 'Owners Residential Zip Code': customer.codepostal,
            'Owners Email': customer.email, 'DL/FEI': customer.fein if selected_owner == '1' and selected_owner != '' else customer.lic,
            'VIN': unit.vin, 'TITLE': unit.title, 'PLATE': unit.irp, 'MAKE': unit.make, 'Year': unit.year,
            'Color': unit.color, 'Weight': unit.empty, 'Gross Vehicle Weight': unit.gross, 'Date': today
        }
        file_name = '82040_mv_{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/82040-mv.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def certificate_mh_title(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/certificate_title.html',
            {
                'customer': customer, 'units': units,
                'certificate_title': 'CERTIFICATE OF MOBILE HOME TITLE',
                'url': 'certificate_mh_title'
            }
        )
    if request.method == 'POST':
        customer = Customers.objects.only('owner', 'owner_surname', 'cusname').get(idcustomer=customer_id)
        selected_owner = request.POST.get('owner')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.get(idunit=request.POST.get('unit'))
        data = {
            "Owner's Name": customer.cusname if selected_owner == '1' and selected_owner != '' else '{0} {1}'.format(customer.owner, customer.owner_surname),
            'Full Name': '{0} {1}'.format(customer.owner, customer.owner_surname),
            "Owner's Phone Number": customer.mobile1, "Owner's Date of Birth": customer.explic.strftime('%m-%d-%Y'),
            "Owner's Mailing Address": customer.address, "Owner's Mailing City": customer.city,
            "Owner's Mailing State": customer.state, "Owner's Mailing Zip Code": customer.codepostal,
            "Owner's Residential Street Address": customer.address, "Owner’s Residential City": customer.city,
            "Owner’s Residential State": customer.state, "Owner’s Residential Zip Code": customer.codepostal,
            "Owner's Email": customer.email, 'Date': today,
            "DL/FEI": customer.fein if selected_owner == '1' and selected_owner != '' else customer.lic,
            "VIN": unit.vin, "Title": unit.title, "Make": unit.make, "Year": unit.year,
        }
        file_name = '82040_mh_{0}.pdf'.format(customer_id)
        generate_pdf_fill('LOCAL/82040-mh.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def separate_odometer(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/separate_odometer.html',
                      {'customer': customer, 'units': units})

    if request.method == 'POST':
        try:
            selected_owner = request.POST.get('owner')
            selected_date = datetime.strptime(request.POST.get('date'), '%m/%d/%Y')
            customer = Customers.objects.get(idcustomer=customer_id)
            unit = Units.objects.get(idunit=request.POST.get('unit'))
            # OWNERS
            owner_name = customer.owner + ' ' + customer.owner_surname
            data = {
                'Vehicle Identification Number': unit.vin if unit.vin is not None else '',
                'Year': unit.year if unit.year is not None else '',
                'Make': unit.make if unit.make is not None else '',
                'Color': unit.color if unit.color is not None else '',
                'Body': unit.type if unit.type is not None else '',
                'Title Number': unit.title if unit.title is not None else '',
                'month': '0%s' % selected_date.month if selected_date.month < 10 else selected_date.month,
                'day': '0%s' % selected_date.day if selected_date.day < 10 else selected_date.day,
                'year': selected_date.year,
                'Buyers Printed Name': customer.cusname if selected_owner == '1' and selected_owner != '' else owner_name,
                'Owners EMail Address': customer.email, 'Buyers Street Address': customer.address, 'City_2': customer.city,
                'State_2': customer.state, 'Zip_2': customer.codepostal,
            }
            # Generate pdf
            file_name = 'separate_odometer{0}.pdf'.format(customer_id)
            generate_pdf_fill('LOCAL/SEPARATE_ODOMETER.pdf', data, file_name)
            return JsonResponse({'filename': file_name})
        except Exception as e:
            return HttpResponse({}, content_type='application/json', status=500)


@login_required(login_url='Procedure:login')
def license_plate(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/license_plate.html',
                      {'customer': customer, 'units': units})

    if request.method == 'POST':
        try:
            selected_date = ''
            if request.POST.get('date'):
                selected_date = datetime.strptime(request.POST.get('date'), '%m/%d/%Y').strftime('%m/%d/%Y')
            customer = Customers.objects.get(idcustomer=customer_id)
            unit = Units.objects.get(idunit=request.POST.get('unit'))
            # OWNERS
            owner_name = customer.owner + ' ' + customer.owner_surname
            data = {
                'Plate': unit.irp if unit.irp is not None else '',
                'Year': unit.year if unit.year is not None else '',
                'Make': unit.make if unit.make is not None else '',
                'Vin': unit.vin if unit.vin is not None else '',
                'Date': selected_date,
                'Printed Name': owner_name,
            }
            # Generate pdf
            file_name = 'license_plate{0}.pdf'.format(customer_id)
            generate_pdf_fill('LOCAL/LICENSE_PLATE.pdf', data, file_name)
            return JsonResponse({'filename': file_name})
        except Exception as e:
            print(e)
            return HttpResponse({}, content_type='application/json', status=500)
        
@login_required(login_url='Procedure:login')
def application_transporter_license_plate(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id)
        return render(request, 'Procedure/Customers/Applications/LOCAL/application_transporter_license_plate.html',
                      {'customer': customer, 'units': units})

    if request.method == 'POST':
        try:
            selected_date = ''
            if request.POST.get('date'):
                selected_date = datetime.strptime(request.POST.get('date'), '%m/%d/%Y').strftime('%m/%d/%Y')
            customer = Customers.objects.get(idcustomer=customer_id)
            unit = Units.objects.get(idunit=request.POST.get('unit'))
            # OWNERS
            name = f'{customer.owner} {customer.owner_surname}' if request.POST.get('owner') == '2' else customer.cusname
            data = {
                'License Plate Numbers Assigned': unit.irp if unit.irp is not None else '',
                'Name of BusinessApplicant': name,
                'Street Address': customer.address if customer.address is not None else '',
                'City State Zip': f'{customer.city}, {customer.state}, {customer.codepostal}' if customer.city and customer.state and customer.codepostal else '',
                'Number of Plates': request.POST.get('number_plates'),
                'Date': selected_date,
            }
            # Generate pdf
            file_name = 'application_transporter_license_plate{0}.pdf'.format(customer_id)
            generate_pdf_fill('LOCAL/83065.pdf', data, file_name)
            return JsonResponse({'filename': file_name})
        except Exception as e:
            print(e)
            return HttpResponse({}, content_type='application/json', status=500)
#END LOCAL


@login_required(login_url='Procedure:login')
def data_unit(request):
    if request.method == 'GET' :
        idunit = int(request.GET.get('unit'))
        unit = Units.objects.only('make', 'year', 'type', 'vin', 'title', 'color', 'empty', 'nounit', 'fuel', 'date',
                                  'gross', 'price', 'idcustomer__dotid', 'idcustomer__fein').get(pk=idunit)
        data = {'make': unit.make, 'year': unit.year, 'type': unit.type, 'vin': unit.vin, 'title': unit.title,
                'gross': unit.gross, 'price': unit.price, 'dotid': unit.idcustomer.dotid, 'fein': unit.idcustomer.fein,
                'color': unit.color, 'empty': unit.empty, 'nounit': unit.nounit, 'fuel': unit.fuel,
                'date': unit.date.strftime('%m/%d/%Y')}
        return JsonResponse(data)


@login_required(login_url='Procedure:login')
def mcs150(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        result = {'customer': customer}
        return render(request, 'Procedure/Customers/Applications/DOT/mcs150.html', result)
    if request.method == 'POST' :
        cargo = request.POST.getlist('cargo')
        reason_button = request.POST.get('type_app')
        milage = request.POST.get('millage') if request.POST.get('millage') else '0'
        today = date.today().strftime("%m/%d/%Y")
        truck = request.POST.get('dump') if request.POST.get('dump') else ''
        othercargo = request.POST.get('othercargo')
        tracktor = request.POST.get('tractors')
        if reason_button == '0':
            reason_button = ''
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'fein', 'ssn', 'address', 'city', 'state', 'codepostal',
                                          'mobile1', 'email', 'corptype', 'dotid', 'mc').get(pk=customer_id)
        if customer.corptype == 'CORP' or customer.corptype == 'INC':
            certifyTitle = 'PRESIDENT'
        elif customer.corptype == 'LLC':
            certifyTitle = 'MGR'
        else:
            certifyTitle = 'OWNER'
        data = {'REASON FOR FILING': reason_button, '1bizName': customer.cusname, '3principalStreet': customer.address,
                '4principalCity': customer.city, '5principalState': customer.state,
                '6principalZip': customer.codepostal, '13bizPhone': customer.mobile1, '20eMail': customer.email,
                '19irsNumber': customer.fein, '16usdotNumber': customer.dotid, '21carrierMileage': milage,
                'officerName1': customer.owner + ' ' + customer.owner_surname, 'certifyName': customer.owner+ ' ' + customer.owner_surname, 'certifyTitle': certifyTitle,
                'certifyDate': today, 'straightOwn': truck, 'tractorOwn': tracktor, '24dd Describe': othercargo}
        if request.POST.get('operations') != 'No':
            drivers = int(request.POST.get('qty_drivers')) if request.POST.get('qty_drivers') else '0'
            if request.POST.get('operations') == 'Inter-State':
                data['INTER'] = 'Yes'
                data['CDLTOTAL'] = drivers
                data['MASINTER'] = drivers
                data['17mcmxNumber'] = customer.mc
            else:
                data['INTRA'] = 'Yes'
                data['CDLTOTAL'] = drivers
                data['MENOSINTRA'] = drivers
        for chk in cargo:
            data[chk] = 'On'
        file_name = 'MCS150{0}.pdf'.format(customer_id)
        generate_pdf_fill('DOT/MCS-150.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


class Clearing_House_Account(View):

    def get(self, request, *args, **kwargs):
        customer = Customers.objects.get(idcustomer=kwargs['customer_id'])
        driver = Drivers.objects.filter(idcustomer=customer.idcustomer, status='Active')
        template = 'Procedure/Customers/Applications/DOT/clearing_house.html'
        return render(request, template, {'customer': customer, 'drivers': driver})

    def post(self, request, *args, **kwargs):
        data = {'DATE': date.today().strftime("%m/%d/%Y")}
        if request.POST.get('account_type') == 'customer':
            customer = Customers.objects.only('cusname', 'dot_user_clearinghouse', 'dot_password_clearinghouse').get(idcustomer = kwargs['customer_id'])
            name = customer.cusname
            username = customer.dot_user_clearinghouse
            password = customer.dot_password_clearinghouse
            certificate_name = kwargs['customer_id']
        if request.POST.get('account_type') == 'driver':
            driver = Drivers.objects.get(iddriver=request.POST.get('driver'))
            name = driver.nombre
            username = driver.username_clearinghouse
            password = driver.password_clearinghouse
            certificate_name = "%s_%s" % (kwargs['customer_id'], request.POST.get('driver'))

        data['CUSTOMER/DRIVER'] = name
        data['USERNAME'] = username if username else ' '
        data['PASSWORD'] = password if password else ' '
        file_name = 'clearing_house_{0}.pdf'.format(certificate_name)
        generate_pdf_fill('DOT/CLEARING_HOUSE_ACCOUNT.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def getCustomers(request, customer_id):
    if request.method == 'GET' :
        type_customer = request.GET.get('type_customer')
        customer = Customers.objects.only('idcustomer', 'cusname', 'owner','owner_surname', 'corptype', 'fein', 'iftaid', 'dotid',
                                          'irpid', 'mobile1', 'address', 'city', 'county', 'state', 'codepostal',
                                          'email').get(pk=customer_id)
        customer_state = States.objects.only('state').get(codestate=customer.state)
        if type_customer == '1':
            if customer.corptype == '--Select--' and customer.corptype == '':
                title = 'OWNER'
            if customer.corptype == 'LLC':
                title = 'MGR'
            else:
                title = 'PRESIDENT'
            data = {'name': customer.cusname, 'fein': customer.fein, 'dotid': customer.dotid, 'irpid': customer.irpid,
                    'phone': customer.mobile1, 'address': customer.address, 'city': customer.city,
                    'county': customer.county,
                    'state': customer_state.state, 'zip': customer.codepostal, 'owner': customer.owner + ' ' + customer.owner_surname,
                    'email': customer.email, 'title': title}
        if type_customer == '2':
            data = {'name': customer.owner + ' ' + customer.owner_surname, 'fein': customer.fein, 'dotid': customer.dotid, 'irpid': customer.irpid,
                    'phone': customer.mobile1, 'address': customer.address, 'city': customer.city,
                    'county': customer.county,
                    'state': customer_state.state, 'zip': customer.codepostal, 'owner': customer.owner + ' ' + customer.owner_surname,
                    'email': customer.email, 'title': 'OWNER'}
        return JsonResponse(data)


@login_required(login_url='Procedure:login')
def irpapp(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('vin', 'idunit')
        millage = Millages.objects.filter(idcustomer=customer_id).only('idmillage', 'year', 'qtr', 'ky', 'nm', 'ny',
                                                                       'total')
        state = States.objects.all()
        return render(request, 'Procedure/Customers/Applications/IRP/newapplication.html',
                      {'customer': customer, 'units': units, 'millages': millage, 'states': state})
    if request.method == 'POST' :
        type_application = request.POST.get('type_application')
        idmilages = request.POST.getlist('idmillage')
        milage_query = ''
        data = {}
        if idmilages:
            for idmilage in idmilages:
                milage_query = idmilage if len(milage_query) == 0 else milage_query + ',' + idmilage
            query = 'SELECT Sum(fl), Sum(al), Sum(ak), Sum(ar), Sum(az), Sum(ca), Sum(co), Sum(ct), Sum(dc), Sum(de), ' \
                    'Sum(ga), Sum(ia), Sum(id), Sum(il), Sum(in1), Sum(ks), Sum(ky), Sum(la), Sum(ma), Sum(md), Sum(me), ' \
                    'Sum(mi), Sum(mn), Sum(mo), Sum(ms), Sum(mt), Sum(nc), Sum(nd), Sum(ne), Sum(nh), Sum(nj),Sum(nm), ' \
                    'Sum(nv), Sum(ny), Sum(oh), Sum(ok), Sum(or1), Sum(pa), Sum(ri), Sum(sc), Sum(sd), Sum(tn), Sum(tx), ' \
                    'Sum(ut), Sum(va), Sum(vt), Sum(wa),Sum(wi), Sum(wv), Sum(wy), Sum(ab), Sum(bc), Sum(mb), Sum(mx), ' \
                    'Sum(nb), Sum(nl), Sum(ns), Sum(nt), Sum(on1), Sum(pe), Sum(qc), Sum(sk), Sum(yt), Sum(total)' \
                    ' FROM millages WHERE idcustomer = {} and idmillage IN ({})'.format(customer_id, milage_query)
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    row = cursor.fetchone()
                except Exception as e:
                    print(e)
                    message = "There are not data"
                    response = JsonResponse({"description": message, "type": "error"})
                    return HttpResponse(response, content_type="application/json", status=500)
            data = {
                'FL': row[0], 'AL': row[1], 'AK': row[2], 'AR': row[3], 'AZ': row[4], 'CA': row[5], 'CO': row[6],
                'CT': row[7], 'DC': row[8], 'DE': row[9], 'GA': row[10], 'IA': row[11], 'ID': row[12], 'IL': row[13],
                'IN': row[14], 'KS': row[15], 'KY': row[16], 'LA': row[17], 'MA': row[18], 'MD': row[19], 'ME': row[20],
                'MI': row[21], 'MN': row[22], 'MO': row[23], 'MS': row[24], 'MT': row[25], 'NC': row[26], 'ND': row[27],
                'NE': row[28], 'NH': row[29], 'NJ': row[30], 'NM': row[31], 'NV': row[32], 'NY': row[33], 'OH': row[34],
                'OK': row[35], 'OR': row[36], 'PA': row[37], 'RI': row[38], 'SC': row[39], 'SD': row[40], 'TN': row[41],
                'TX': row[42], 'UT': row[43], 'VA': row[44], 'VT': row[45], 'WA': row[46], 'WI': row[47], 'WV': row[48],
                'WY': row[49], 'AB': row[50], 'BC': row[51], 'MB': row[52], 'MX': row[53], 'NB': row[54], 'NL': row[55],
                'NS': row[56], 'NT': row[57], 'ON': row[58], 'PE': row[59], 'QC': row[60], 'SK': row[61], 'YT': row[62],
                'TOTAL': row[63]
            }
        irp = request.POST.get('irp') if request.POST.get('irp') != '' else 'NEW ACCOUNT'
        today = date.today()
        data['TYPE APPLICATION'] = type_application
        data['CUSNAME'] = request.POST.get('name')
        data['ADDRESS'] = request.POST.get('address')
        data['APPLICANT MAILING ADDRESS'] = request.POST.get('address')
        data['CITY'] = request.POST.get('city')
        data['COUNTY'] = request.POST.get('county')
        data['STATE'] = request.POST.get('state')
        data['ZIPCODE'] = request.POST.get('zip')
        data['PHONE'] = request.POST.get('phone')
        data['EMAIL'] = request.POST.get('email')
        data['IRP'] = irp
        data['DOT'] = request.POST.get('dotid_customer')
        data['FEIN'] = request.POST.get('fein')
        data['REGYEAR'] = today.year
        data['PRINTED NAME'] = request.POST.get('owner')
        data['TITLE'] = request.POST.get('title')
        data['DATE'] = today.strftime('%m/%d/%Y')
        safely_list = request.POST.getlist('safely')
        count = 0
        for safely in safely_list:
            request_type = request.POST.getlist('type')[count]
            data['TTYPE{0}'.format(count)] = request.POST.getlist('transaction')[count]
            data['UNIT{0}'.format(count)] = request.POST.getlist('nounit')[count]
            data['YEAR{0}'.format(count)] = str(request.POST.getlist('year')[count])[2:]
            data['MAKE{0}'.format(count)] = request.POST.getlist('make')[count]
            data['VIN{0}'.format(count)] = request.POST.getlist('vin')[count]
            data['TYPE{0}'.format(count)] = request_type
            data['AXLESPOWER{0}'.format(count)] = 2 if request_type == 'TK' else 3
            data['AXLESTRAILER{0}'.format(count)] = 2
            data['FUEL{0}'.format(count)] = str(request.POST.getlist('fuel')[count])[0:1]
            data['COLOR{0}'.format(count)] = request.POST.getlist('color')[count]
            data['GROSS{0}'.format(count)] = request.POST.getlist('gross')[count]
            data['EMPTY{0}'.format(count)] = request.POST.getlist('empty')[count]
            data['DATEP{0}'.format(count)] = request.POST.getlist('date')[count]
            data['PRICE{0}'.format(count)] = request.POST.getlist('price')[count]
            data['TITLE{0}'.format(count)] = request.POST.getlist('title_unit')[count]
            data['DOT{0}'.format(count)] = request.POST.getlist('dotid')[count]
            data['FEIN{0}'.format(count)] = request.POST.getlist('fein_unit')[count]
            data['YES_{0}'.format(count)] = 'On' if safely == 'true' else 'Off'
            data['NO_{0}'.format(count)] = 'On' if safely == 'false' else 'Off'
            count += 1
        while count <= 5:
            data['NO_{0}'.format(count)] = 'On'
            count += 1
        data['FLEET NUMBER'] = len(safely_list)
        file_name = 'irpapp{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/IRPAPP.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def irp_transfers(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        result = {'customer': customer, 'units': units}
        return render(request, 'Procedure/Customers/Applications/IRP/transfer_letter.html', result)
    if request.method == 'POST' :
        today = date.today().strftime("%m/%d/%Y")
        idunit = int(request.POST.get('unit'))
        idunit_to = int(request.POST.get('unit_to'))
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'irpid').get(pk=customer_id)
        unit = Units.objects.only('year', 'make', 'vin', 'irp').get(idcustomer=customer_id, idunit=idunit)
        unit_to = Units.objects.only('year', 'make', 'vin', 'irp').get(idcustomer=customer_id, idunit=idunit_to)
        data = {'DATE': today, 'CUSTOMER': customer.cusname, 'IRP': customer.irpid, 'OWNER': customer.owner + ' ' + customer.owner_surname,
                'YEAR': unit.year,
                'MAKE': unit.make, 'VIN': unit.vin, 'PLATE': unit.irp, 'YEAR2': unit_to.year, 'MAKE2': unit_to.make,
                'VIN2': unit_to.vin}
        file_name = 'IRPTRANSFERS{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/IRPTRANSFERS.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def irp_nonuse(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/IRP/irpnonuse.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        date_from = request.POST.get('from')
        date_thru = request.POST.get('thru')
        today = date.today()
        unit = Units.objects.only('type', 'year', 'make', 'vin', 'idcustomer__irpid', 'idcustomer__cusname').get(
            idunit=idunit)
        data = {'CUSTOMER': unit.idcustomer.cusname, 'IRP': unit.idcustomer.irpid, 'MAKE': unit.make,
                'VIN': unit.vin, 'YEAR': today.strftime('%y'), 'MONTH': today.strftime('%B'), 'DAY': today.strftime('%d'),
                'FROM': date_from, 'THRU': date_thru, 'DATE': today.strftime("%m/%d/%Y")}
        file_name = 'nonuse{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/NONUSE-AFFIDAVIT.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def irp_prepass(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'nounit', 'year', 'make', 'vin',
                                                                  'irp').order_by('-status')
        return render(request, 'Procedure/Customers/Applications/IRP/prepass.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST' :
        idunits = request.POST.getlist('idunit')
        application = request.POST.get('application')
        today = date.today().strftime('%m/%d/%Y')
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'email', 'mobile1', 'fax', 'address', 'city', 'state',
                                          'codepostal', 'dotid', 'irpid', 'prepass').get(pk=customer_id)
        #state = States.objects.only('codestate').get(state=customer.state)
        data = dict(CUSNAME=customer.cusname, DOT=customer.dotid, DATE=today)
        data['OWNER'] = customer.owner + ' ' + customer.owner_surname
        data['PHONE'] = customer.mobile1
        data['ADDRESS'] = customer.address
        data['CITY'] = customer.city
        data['STATE'] = customer.state
        data['ZIPCODE'] = customer.codepostal
        data['EMAIL'] =  customer.email if customer.email else ''
        if customer.prepass == '':
            data['NEW'] = 'On'
            data['EXISTING'] = 'Off'
        else:
            data['NEW'] = 'Off'
            data['EXISTING'] = 'On'
            data['ACCOUNT'] = customer.prepass if customer.prepass else ''
        data['FAX'] = customer.fax if customer.fax else '800-920-4857'
        if application == '1':
            data['PREPASS'] = 'On'
        if application == '2':
            data['PREPASSPLUS'] = 'On'
        if application == '3':
            data['TOLLS'] = 'On'
        count = 0
        for idunit in idunits:
            unit = Units.objects.only('nounit', 'irp', 'vin', 'year', 'make', 'irp').get(pk=idunit)
            unitNo = 'UNITNO{0}'.format(count)
            data[unitNo] = unit.nounit
            tag = 'TAG{0}'.format(count)
            data[tag] = unit.irp
            vin = 'VIN{0}'.format(count)
            data[vin] = unit.vin
            year = 'YEAR{0}'.format(count)
            data[year] = unit.year
            make = 'MAKE{0}'.format(count)
            data[make] = unit.make
            irp = 'IRP{0}'.format(count)
            data[irp] = customer.irpid
            statetag = 'STATETAG{0}'.format(count)
            data[statetag] = customer.state
            count = count + 1

        file_name = 'PREPASS{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/PREPASS.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def irp_texas(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('cusname', 'irpid', 'iftaid').get(pk=customer_id)
        today = date.today().strftime('%m/%d/%Y')
        data = {
            'Registrant Name': customer.cusname, 'Street Address': customer.address, 'Zip Code': customer.codepostal,
            'State': customer.state if customer.state else '', 'City': customer.city, 'Phone Number': customer.mobile1,
            'Email Address': customer.email,
            'Date': today
        }
        file_name = 'irptexas{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/MCD358.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def irp_85100(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id).only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/IRP/irp_85100.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        customer = Customers.objects.only('cusname', 'dotid', 'irpid').get(idcustomer=customer_id)
        unit = Units.objects.only('type', 'year', 'make', 'vin', 'irp').get(idunit=idunit)
        data = {'Print Registrant Name': customer.cusname, 'IRP Account Number': customer.irpid if customer.irpid else '',
                'DOT Number': customer.dotid if customer.dotid else '',
                'Year': unit.year, 'Make': unit.make, 'Body': unit.type if unit.type else '',
                'Title Number': unit.title if unit.title else '', 'Plate Number': unit.irp if unit.irp else '',
                'Unit Number': unit.nounit if unit.nounit else ''}
        file_name = 'irp85100_{0}.pdf'.format(customer_id)
        generate_pdf_fill('IRP/85100.pdf', data, file_name)
        return JsonResponse({'filename': file_name})
# END IRP


@login_required(login_url='Procedure:login')
def other_poa(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/OTHER/poa.html', {'customer': customer})
    if request.method == 'POST' :
        customer = Customers.objects.only('cusname', 'fein', 'ssn', 'mobile1', 'email', 'irpid', 'iftaid', 'owner', 'owner_surname').get(
            pk=customer_id)
        rbgroup = request.POST.get('rbgroup')
        title = request.POST.get('title')
        selected_date = request.POST.get('date')
        if selected_date is None or selected_date == "":
            selected_date = date.today().strftime('%m/%d/%Y')
            month_year = '{0} {1}'.format(date.today().strftime('%B'), date.today().year)
            assign_day = date.today().day
        else:
            selected_date = datetime.strptime(selected_date, "%m/%d/%Y")
            month_year = "{0} {1}".format(selected_date.strftime('%B'), selected_date.year)
            assign_day = selected_date.day
            selected_date = selected_date.strftime("%m/%d/%Y")

        fein_or_ssn = customer.ssn if customer.fein == '' else customer.fein
        data = {'Name of Account': customer.cusname, 'Account Name': customer.cusname,
                'AREAT': customer.mobile1[0:3] if customer.mobile1 else '', 'Telephone': customer.mobile1[4:] if customer.mobile1 else '',
                'Email': customer.email, 'Date': selected_date, 'Principal Name': customer.owner + ' ' + customer.owner_surname, 'Title': title,
                'DAY': assign_day, 'MONTH': month_year, 'AFN1': '{0}'.format(selected_date),
                'AFN2': customer.state if customer.state else '','FEIN': fein_or_ssn if fein_or_ssn else ''}
        if rbgroup == '1':
            data['IRP Account Number'] = 'NEW ACCOUNT'
            data['IFTA Account Number'] = ''
        if rbgroup == '2':
            data['IRP Account Number'] = customer.irpid if customer.irpid else ''
            data['IFTA Account Number'] = 'NEW ACCOUNT'
        if rbgroup == '3':
            data['IRP Account Number'] = customer.irpid if customer.irpid else ''
            data['IFTA Account Number'] = customer.iftaid
        if customer.corptype == '--Select--' or customer.corptype == '':
            data['INDIVIDUAL'] = 'On'
            data['COMPANY'] = 'Off'
        else:
            data['INDIVIDUAL'] = 'Off'
            data['COMPANY'] = 'On'
        file_name = 'POA{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/POA.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def other_keeping(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/OTHER/keeping.html', {'customer': customer})
    if request.method == 'POST' :
        customer = Customers.objects.only('owner', 'owner_surname', 'irpid', 'iftaid', 'lic').get(pk=customer_id)
        rbgroup = request.POST.get('rbgroup')
        year = str(date.today().year)
        data = {'OWNER': customer.owner + ' ' + customer.owner_surname, 'TITLE': 'OWNER',
                'IDENTIFICATION': customer.lic, 'DATE': date.today().strftime('%m/%d/%Y'),
                'DAY': date.today().strftime('%d'), 'MONTH': date.today().strftime('%B'), 'YEAR': year[-2:]}
        if rbgroup == '1':
            data['IRP'] = 'NEW ACCOUNT'
            data['IFTA'] = ''
        if rbgroup == '2':
            data['IRP'] = customer.irpid
            data['IFTA'] = 'NEW ACCOUNT'
        if rbgroup == '3':
            data['IRP'] = customer.irpid
            data['IFTA'] = customer.iftaid
        file_name = 'KEEPING{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/KEEPING.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_efile(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('cusname', 'irpid', 'iftaid', 'owner', 'owner_surname').get(pk=customer_id)
        today = date.today().strftime('%m/%d/%Y')
        data = {'CUSNAME': customer.cusname, 'IRP': customer.irpid, 'IFTA': customer.iftaid,
                'EMAIL': 'INFO@DIRECTSOLUTIONSERVICES.COM',
                'OWNER': customer.owner + ' ' + customer.owner_surname, 'TITLE': 'OWNER', 'DATE': today}
        file_name = 'EFILE{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/EFILE2021.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_lease(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active')
        return render(request, 'Procedure/Customers/Applications/OTHER/lease_agreement.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST' :
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'opercomp').get(pk=customer_id)
        date = request.POST.get('date')
        data = {}
        if date == '':
            date = datetime.today()
            data['DAY'] = date.day
            data['MONTH'] = date.strftime('%B')
            data['YEAR P'] = date.year
        else:
            date = datetime.strptime(date, '%m/%d/%Y').date()
            data['DAY'] = date.day
            data['MONTH'] = date.strftime('%B')
            data['YEAR P'] = date.year
        data['LESSOR'] = customer.owner + ' ' + customer.owner_surname if request.POST.get('lessor') == '2' else customer.cusname
        data['LESSEE'] = customer.opercomp if customer.opercomp else ''
        second_line = ""
        if customer.dotid:
            second_line = 'DOT: %s' % customer.dotid
        if customer.fein:
            second_line += 'TAX ID: %s' % customer.fein
        data['CUSTOMER'] = "%s \n %s \n %s \n %s, %s %s"% (customer.cusname, second_line, customer.address, customer.city, customer.state, customer.codepostal)
        data['PERIOD'] = "{0} to {1}".format(request.POST.get('date'),request.POST.get('date_end'))
        unit_request = request.POST.getlist('idunit')
        count = 0
        for idunit in unit_request:
            unit = Units.objects.only('nounit', 'year', 'make', 'vin', 'type').get(pk=idunit)
            nounit = 'UNIT{0}'.format(count)
            year = 'YEAR{0}'.format(count)
            make = 'MAKE{0}'.format(count)
            vin = 'VIN{0}'.format(count)
            type = 'TYPE{0}'.format(count)
            data[nounit] = unit.nounit
            data[year] = unit.year
            data[make] = unit.make
            data[vin] = unit.vin
            data[type] = unit.type
            count = count + 1

        file_name = 'LEASE{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/LEASE.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_mcd356texas(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active')
        return render(request, 'Procedure/Customers/Applications/OTHER/mcd_356_texas.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST' :
        customer = Customers.objects.only('cusname', 'ssn', 'fein', 'contact1', 'mobile1', 'mobile2', 'email', 'city', 'state', 'codepostal', 'county', 'address', 'dotid').get(pk=customer_id)
        date = request.POST.get('date')
        data = {}
        if date == '':
            date = datetime.today()
            data['Date'] = date.strftime('%m/%d/%Y')
            data['Reg Year'] = date.year
        else:
            date = datetime.strptime(date, '%m/%d/%Y').date()
            data['Date'] = date
            data['Reg Year'] = date.year
        data['Account Name'] = customer.cusname
        data['adress'] = customer.address
        data['county'] = customer.county if customer.county else ''
        data['city state zipcode'] = "%s %s %s" % (customer.city, customer.state, customer.codepostal)
        data['Contact Person'] = customer.contact1
        data['Phone No'] = customer.mobile1 if customer.mobile1 else ''
        data['Email Address'] = customer.email if customer.email else ''
        data['Secondary Phone No'] = customer.mobile2 if customer.mobile2 else ''
        data['TaxID'] = customer.fein if customer.fein else customer.ssn
        data['DOT'] = customer.dotid if customer.dotid else ''
        unit_request = request.POST.getlist('idunit')
        count = 1
        for idunit in unit_request:
            unit = Units.objects.only('nounit', 'year', 'make', 'vin', 'type', 'gross').get(pk=idunit)
            nounit = 'Unit Row{0}'.format(count)
            year = 'YearRow{0}'.format(count)
            make = 'MakeRow{0}'.format(count)
            vin = 'VINRow{0}'.format(count)
            type = 'Type Row{0}'.format(count)
            gross = 'Gross WgtRow{0}'.format(count)
            fuel = 'Fuel Row{0}'.format(count)
            price = 'Purchase PriceRow{0}'.format(count)
            dateprice = 'Purchase DateRow{0}'.format(count)
            data[nounit] = unit.nounit
            data[year] = unit.year
            data[make] = unit.make
            data[vin] = unit.vin
            data[type] = unit.type if unit.type != 'No' else ''
            data[gross] = unit.gross
            data[fuel] = unit.fuel
            data[price] = unit.price
            data[dateprice] = unit.date.strftime('%m/%d/%Y')
            count = count + 1
        file_name = 'mcd-356-texas{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/mcd-356-texas-form.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_crttitle(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/OTHER/certificate_title.html',
                      {'customer': customer, 'units': units, 'today': datetime.today().strftime('%m/%d/%Y')})
    if request.method == 'POST' :
        vin = str(request.POST.get('vin'))
        date_frm = str(request.POST.get('date'))
        name = str(request.POST.get('name'))
        customer = Customers.objects.only('owner', 'owner_surname', 'email', 'lic', 'explic', 'address', 'city', 'state', 'codepostal').get(pk=customer_id)
        if name == "owner":
            name = customer.owner + ' ' + customer.owner_surname
            fldl = customer.lic
        else:
            name = customer.cusname
            fldl = customer.fein
        data = {'Unit Number': str(request.POST.get('nounit')), 'owner name': name, 'Owner Date of Birth': customer.explic.strftime('%m/%d/%Y'), 'FL DL/FEID#': fldl,
                'owner email': customer.email,'owner mailing add': customer.address, 'city': customer.city, 'st':customer.state, 'zip':customer.codepostal, 'VIN': vin, 'VIN3': vin,
                'Today Date':date_frm, 'Date of Applicant (Owner) Signature': date_frm,'make': str(request.POST.get('make')), 'MV-MH-Ves-year': str(request.POST.get('year')),
                'color': str(request.POST.get('color')), 'FL title number 1': str(request.POST.get('title')), 'gvw/loc': str(request.POST.get('gross')),
                'wgt': str(request.POST.get('empty')), 'Choose One Application Type': str(request.POST.get('Application-Type'))}
        file_name = 'crtTitle{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/82040.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_vin_verification(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/other/vin_verification.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.only('type', 'year', 'make', 'vin', 'irp').get(idunit=idunit)
        data = {
            'Date - Part A': today, 'Date - Part B': today,
            'VIN': unit.vin, 'Year': unit.year, 'Make': unit.make, 'Body Type': unit.type if unit.type else '',
        }
        file_name = 'vinverification_{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/VINVerification.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_general_affidavit(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/OTHER/general_affidavit.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.only('year', 'make', 'vin', 'title','idcustomer__irpid', 'idcustomer__cusname').get(
            idunit=idunit)
        data = {'CUSTOMER': unit.idcustomer.cusname, 'MAKE': unit.make, 'YEAR': unit.year, 'VINHIN': unit.vin, 'TITLE': unit.title, 'DATE': today}
        file_name = 'general-affidavit{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/general-affidavit.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_annual_vehicle_inspection(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/OTHER/annual_vehicle_inspection.html',
                      {'customer': customer, 'units': units})
    if request.method == 'POST':
        idunit = request.POST.get('unit')
        today = date.today().strftime("%m/%d/%Y")
        unit = Units.objects.only('year', 'make', 'vin', 'title','idcustomer__irpid', 'idcustomer__cusname').get(
            idunit=idunit)
        cszc = unit.idcustomer.city + " " + unit.idcustomer.state + " " + unit.idcustomer.codepostal
        data = {'MOTOR CARRIER OPERATOR': unit.idcustomer.cusname, 'ADDRESS': unit.idcustomer.address, 'CITY STATE ZIP CODE': cszc,
                'VEHICLE INFORMATION': unit.vin, 'FLEET UNIT NUMBER': unit.nounit, 'DATE': today, 'VIDENTIFICATION': 'VIN'}
        file_name = 'annual_vehicle_inspection{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/ANNUAL_VEHICLE_INSPECTION_REPORT.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def other_florida_quit_claim_deed(request, customer_id):
    customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
    if request.method == 'GET':
        return render(request, 'Procedure/Customers/Applications/OTHER/florida_quit_claim_deed.html',
                      {'customer': customer})
    if request.method == 'POST':
        today = date.today()
        data = {
            'PARCEL NUMBER': request.POST.get('parcel'), 'DAY': today.strftime('%d'), 'MONTH': today.strftime('%B'),
            'YEAR': today.strftime('%y'), 'CUSTOMER': customer.owner + " " + customer.owner_surname,
            'STATUS GRANTOR': request.POST.get('status_grantor').upper(),
            'ADDRESS': customer.address + ", " + customer.city + ", " + customer.state + " " + customer.codepostal,
            'GRANTEE': request.POST.get('grantee'), 'SELECT ONE': request.POST.get('select_grantee').upper(),
            'ADDRESS GRANTEE': request.POST.get('address_grantee'),
            'AMOUNT': request.POST.get('amount')
        }
        file_name = 'florida_quit_claim_deed{0}.pdf'.format(customer_id)
        generate_pdf_fill('OTHER/Quit_Claim_Deed_Form.pdf', data, file_name)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def other_replacementLicensePlateValidationDecalParkingPermit(request, customer_id):
    customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
    if request.method == 'GET':
        units = Units.objects.filter(idcustomer=customer_id, status='Active').only('idunit', 'vin')
        return render(request, 'Procedure/Customers/Applications/OTHER/replacementLicenseplate_validationDecal_parkingpermit.html',
                      {'customer': customer, 'units':units})
        
    if request.method == 'POST':
        today = date.today()
        selected_unit = request.POST.get('unit')
        if selected_unit is not None:
            unit = Units.objects.only('year', 'make', 'vin', 'title','idcustomer__irpid', 'idcustomer__cusname').get(
                idunit=selected_unit)
            data = {
                'Owners': customer.owner + " " + customer.owner_surname,
                'DLN': customer.lic,
                'Address': customer.address,
                'City': customer.city, 
                'State':customer.state,  'Zip':customer.codepostal,
                'VIN': unit.vin, 'Make': unit.make, 'Year': unit.year, 'PLATE': unit.irp,
                'Date': today.strftime('%m/%d/%Y')
            }
            file_name = 'hsmv83146{0}.pdf'.format(customer_id)
            generate_pdf_fill('OTHER/REPLACEMENT_LICENSE_PLATE.pdf', data, file_name)
            return JsonResponse({'filename': file_name})
        else:
            message = JsonResponse({'description': 'Please select a unit.', 'type': 'error'})
            return HttpResponse(message, content_type="application/json", status=500)

@login_required(login_url='Procedure:login')
def permits_ny(request, customer_id):
    if request.method == 'GET' :
        today = datetime.today().strftime('%m/%d/%Y')
        customer = Customers.objects.only('fein', 'ssn', 'dotid', 'mobile1', 'cusname', 'owner','owner_surname', 'address', 'city',
                                          'state', 'codepostal', 'corptype').get(pk=customer_id)
        data = {'FEIN': customer.fein, 'SSN': customer.ssn, 'DOT': customer.dotid, 'PHONE': customer.mobile1,
                'CUSTOMER': customer.cusname, 'OWNER': customer.owner + ' ' + customer.owner_surname, 'ADDRESS': customer.address,
                'CITY': customer.city,
                'STATE': customer.state, 'ZIP': customer.codepostal, 'DATE': today}
        if customer.corptype == '' or customer.corptype == '--Select--':
            data['PERSONAL'] = 'ON'
            data['TITLE'] = 'OWNER'
        if customer.corptype == 'CORP':
            data['CORP'] = 'ON'
            data['TITLE'] = 'PRESIDENT'
        if customer.corptype == 'INC':
            data['CORP'] = 'ON'
            data['TITLE'] = 'PRESIDENT'
        if customer.corptype == 'LLC':
            data['LLC'] = 'ON'
            data['TITLE'] = 'MGR'
        file_name = 'ny{0}.pdf'.format(customer_id)
        generate_pdf_fill('PERMITS/NY.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def permits_nj(request, customer_id):
    if request.method == 'GET' :
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/PERMITS/NJ.html', {'customer': customer})
    if request.method == 'POST' :
        customer = Customers.objects.only('cusname', 'owner','owner_surname', 'fein', 'ssn', 'address', 'city', 'state', 'codepostal',
                                          'mobile1', 'email', 'corptype').get(pk=customer_id)
        date_begin = request.POST.get('date')
        typecargo = request.POST.get('typecargo')
        if date_begin == '':
            message = JsonResponse({'description': 'Date begin is empty', 'type': 'error'})
            return HttpResponse(message, content_type='application/json', status=500)
        else:
            date_begin = datetime.strptime(date_begin, '%m/%d/%Y').date()
        date_today = datetime.today()
        state = States.objects.only('codestate', 'state').get(codestate=customer.state)
        address = "{0},{1} {2}".format(customer.city, state, customer.codepostal)
        data = {'CUSTOMER': customer.cusname, 'ADDRESS': customer.address, 'CITY': customer.city,
                'OWNER': customer.owner + " " + customer.owner_surname, 'SSN': customer.ssn, 'FEIN': customer.fein, 'PHONE': customer.mobile1,
                'EMAIL': customer.email,
                'DATE': date_today.strftime('%m/%d/%Y'), 'PRODUCT': typecargo, 'ADDRESS2': address,
                'DAY1': date_begin.day, 'MONTH1': date_begin.month, 'YEAR1': date_begin.year, 'DAY2': date_today.day,
                'MONTH2': date_today.month, 'YEAR2': date_today.year}
        corptype = customer.corptype
        if corptype == '--Select--' or corptype == '':
            data['SOLE'] = 'Yes'
            data['TITLE'] = 'OWNER'
        if corptype == 'CORP' or corptype == 'INC':
            data['CORP'] = 'Yes'
            data['TITLE'] = 'PRESIDENT'
        if corptype == 'LLC':
            data['LLC'] = 'Yes'
            data['TITLE'] = 'MGR'
        for k in range(5):
            zip = customer.codepostal
            if zip.isnumeric():
                zip_no = 'ZIP{0}'.format(k)
                data[zip_no] = zip[k]
        fein = customer.fein if customer.fein else ''
        if len(fein) != 0:
            position = 0
            for i in range(len(fein)):
                fein_form = 'FEIN{0}'.format(position)
                if fein[i].isnumeric():
                    position += 1
                    data[fein_form] = fein[i]
        ssn = customer.ssn if customer.ssn else ''
        if len(ssn) != 0:
            position = 0
            for i in range(len(ssn)):
                ssn_form = 'SSN{0}'.format(position)
                if ssn[i].isnumeric():
                    position += 1
                    data[ssn_form] = ssn[i]
        file_name = 'nj{0}.pdf'.format(customer_id)
        generate_pdf_fill('PERMITS/NJ.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def permits_nm(request, customer_id):
    today = date.today()
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        start_period = "01/01/%s" % (today.year)
        end_period = "12/31/%s" % (today.year)
        return render(request, 'Procedure/Customers/Applications/PERMITS/NM.html',
                      {'customer': customer, 'start_period': start_period, 'end_period': end_period})
    if request.method == 'POST':
        customer = Customers.objects.only('cusname', 'owner', 'owner_surname', 'dotid', 'irpid').get(idcustomer=customer_id)
        data = {
            'Names': customer.cusname, 'Mailing Address': customer.address, 'City': customer.city, 'State': customer.state,
            'Zip Code': customer.codepostal, 'Email Address': customer.email, 'Fax Number': customer.fax if customer.fax else '',
            'Telephone Number': customer.mobile1 if customer.mobile1 else customer.mobile2, 'FEIN': customer.fein if customer.fein else '',
            'Printed Name': customer.owner + ' ' + customer.owner_surname if customer.owner  else '', 'Date': today.strftime('%m/%d/%Y'), 'Date_2': today.strftime('%m/%d/%Y'),
            'Starting Period': request.POST.get('start_period'), 'Ending Period': request.POST.get('end_period')
        }
        file_name = 'nmpermit_{0}.pdf'.format(customer_id)
        generate_pdf_fill('PERMITS/NM.pdf', data, file_name)
        return JsonResponse({'filename': file_name})


@login_required(login_url='Procedure:login')
def permits_overweight_oversize(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/PERMITS/overweight_oversize.html',
                      {'customer': customer})
    if request.method == 'POST':
        axles = request.POST.get('axles')
        template_name = 'TRUCK_DIMENSIONS_{0}_AXLES.pdf'.format(axles)
        path_template = '{0}/PERMITS/OVERWEIGHT_OVERSIZE/{1}'.format(settings.TEMPLATES_PDF, template_name)
        file_name = 'truck_dimensions_{0}.pdf'.format(customer_id)
        path_destination = '{0}/{1}'.format(settings.FILES_PDF, file_name)
        shutil.copy(path_template, path_destination)
        return JsonResponse({'filename': file_name})

@login_required(login_url='Procedure:login')
def labcorp(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        drivers = Drivers.objects.filter(idcustomer=customer_id, status='Active').order_by("-iddriver")
        return render(request, 'Procedure/Customers/Applications/DOT/labcorp.html',
                      {'customer': customer, 'drivers': drivers})
        
    if request.method == 'POST':
        try:
            customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
            
            labcorp_form = request.POST.get('form')
            date_selected = request.POST.get('select_date')
            data = {}
            if labcorp_form == 'preemployment' or labcorp_form == 'drug':
                if request.POST.get('drivers') == '--SELECT--':
                    return MessageResponse(description="The driver is required", data={}).warning()
                driver = Drivers.objects.get(iddriver=request.POST.get('drivers'))
                data = {
                    "Company Name": customer.cusname,
                    "Driver Name": driver.nombre,
                    "Date": date_selected,
                    "SSN": driver.ssn,
                }
                template_name = 'LAB_TEST_PRE_EMPLOYMENT.pdf' if labcorp_form == 'preemployment' else 'LABCORP_TESTDRUG.pdf'
            else:
                template_name = 'LAB_CORP_ALCOHOL_TEST.pdf'
            path_file = f'/DOT/LABCORP/{template_name}'
            file_name = '{0}_{1}.pdf'.format(labcorp_form, customer_id)
            generate_pdf_fill(path_file, data, file_name)
            return JsonResponse({'filename': file_name})
        except Exception as e:
            return MessageResponse(description='Check the data', data={}).warning()
    
    
class BillSaleInterstate(View):
    def get(self, request, *args, **kwargs):
        if request.method == 'GET' :
            if request.GET:
                unit = Units.objects.only('year', 'vin', 'make', 'price').get(idunit=request.GET['unit'])
                return JsonResponse({'year': unit.year, 'vin': unit.vin, 'make': unit.make, 'price': unit.price }, safe=False)
            customer = Customers.objects.only('idcustomer', 'cusname').get(pk=kwargs['customer_id'])
            units = Units.objects.filter(idcustomer=kwargs['customer_id'], status='Active')
            return render(request, 'Procedure/Customers/Applications/OTHER/bill_sale_interstate.html',
                          {'customer': customer, 'units': units})

    def post(self, request, **kwargs):
        if request.method == 'POST' :
            data = {'Identification no': request.POST.get('vin'), 'Yr Model': request.POST.get('year'), 'Make': request.POST.get('make'),
                    'Selling Price': request.POST.get('price')}
            file_name = 'saleinterstate{0}.pdf'.format(kwargs['customer_id'])
            generate_pdf_fill('OTHER/reg135.pdf', data, file_name)
            return JsonResponse({'filename': file_name})


class Certificate_Enrollment_Alcohol_Drug(View):

    def get(self, request, *args, **kwargs):
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=kwargs['customer_id'])
        return render(request, 'Procedure/Customers/Applications/DOT/certificate_random_test.html', {
            'customer': customer, 'title_certificate_random': 'Certificate Alcohol & Drug', 'urlcertificate': 'certificate_enrollment_alcohol_drug'
        })

    def post(self, request, *args, **kwargs):
        if request.method == 'POST' :
            customer = Customers.objects.get(idcustomer=kwargs['customer_id'])
            effective_date = datetime.strptime(str(request.POST.get('effective_date')), '%m/%d/%Y').date()
            expiration_date = datetime.strptime('%s-12-31'%effective_date.year, '%Y-%m-%d').date()
            data = {'cusname': customer.cusname, 'effective date': effective_date.strftime('%B %d, %Y'), 'expiration date': expiration_date.strftime('%B %d, %Y')}
            file_name = '{0}_CERTIFICATE_ENROLLMENT.pdf'.format(kwargs['customer_id'])
            # file_name = '{0}_CERTIFICATE_ENROLLMENT.pdf'.format(customer.cusname.replace(" ","_"))
            generate_pdf_fill('CERTIFICADO_ALCOHOL_DRUG.pdf', data, file_name)
            return JsonResponse({'filename': file_name})


def generate_pdf_fill(template_name, data, file_name, flatten=False):
    path_template = settings.TEMPLATES_PDF + '/' + template_name
    template = FileSystemStorage(location=path_template)
    out_file = settings.FILES_PDF + '/' + file_name
    pypdftk.fill_form(template.location, data, out_file, flatten=flatten)


@login_required(login_url='Procedure:login')
def get_file(request, name):
    file_name = settings.FILES_PDF + '/{0}'.format(name)
    tmp = open(file_name, 'rb')
    return FileResponse(tmp)


class GeneratePDF(View):

    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    def get(self, request, *args, **kwargs):
        invoice_id = self.kwargs['idinvoice']
        download = self.request.GET.get('download', False)        
        try:
            html = self.Create_PDF(request, invoice_id)
            response = HttpResponse(content_type='application/pdf')
            response['Cache-Control'] = 'max-age=0'
            response['Accept-Ranges'] = 'none'

            if download == 'True':
                response['Content-Disposition'] = 'attachment; filename="invoice{}.pdf"'.format(invoice_id)
            else:
                response['Content-Disposition'] = 'inline; filename=invoice{}.pdf'.format(invoice_id)

            pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)
            return response
        except Exception as e:
            print(e)
            return HttpResponse("Error making the file")

    @staticmethod
    def Create_PDF(request, invoice_id):
        details_invoice = Invoice_det.objects.select_related("idinvoice__idcustomer").filter(idinvoice=invoice_id) \
            .only("idinvoice", "code__idservice", "service", "quantity", "rate", "discount", "amount", "coments", "idinvoice",
                  "discountype",
                  "idinvoice__invdate", "idinvoice__amount", "idinvoice__idcustomer", "idinvoice__status",
                  "idinvoice__deu",
                  "idinvoice__idcustomer__cusname", "idinvoice__idcustomer__address", "idinvoice__idcustomer__city",
                  "idinvoice__idcustomer__state", "idinvoice__idcustomer__codepostal", "idinvoice__idcustomer__mobile1"
                  )
        invoice = details_invoice.first().idinvoice
        invoice.invdate = invoice.invdate.strftime("%m/%d/%Y")
        customer = invoice.idcustomer
        Paid = {"datepaid": '', "total_paid": '0', "check": '0', "cash": '0',
                "credit_card": '0', 'zelle': '0'}
        try:
            total_paid = Invoice_paid.objects.filter(idinvoice=invoice_id).aggregate(total=Sum("paid"))
            check = Invoice_paid.objects.filter(idinvoice=invoice_id, typepaid="Check").aggregate(check=Sum("paid"))
            cash = Invoice_paid.objects.filter(idinvoice=invoice_id, typepaid="Cash").aggregate(cash=Sum("paid"))
            credit_card = Invoice_paid.objects.filter(idinvoice=invoice_id, typepaid="Credit Card").aggregate(
                credit_card=Sum("paid"))
            zelle = Invoice_paid.objects.filter(idinvoice=invoice_id, typepaid="Zelle").aggregate(
                zelle=Sum("paid"))
            datepaid = Invoice_paid.objects.only("datepaid").filter(idinvoice=invoice_id).latest('datepaid')
            datepaid = datepaid.datepaid.strftime('%m/%d/%Y')
            Paid = {"datepaid": datepaid, "total_paid": total_paid["total"], "check": check["check"],
                    "cash": cash["cash"], "zelle": zelle["zelle"],
                    "credit_card": credit_card["credit_card"]}
        except Exception as e:
            pass
        template = get_template('PDF/template_invoice.html')
        context = {"details": details_invoice, "invoice": invoice, "customer": customer,
                   "customer_id": invoice.idcustomer_id, "Paid": Paid,
                   'logo': '{}{}'.format(settings.STATIC_ROOT, '/img/logo-01.png'),
                   'payment': '{}{}'.format(settings.STATIC_ROOT, '/img/payment.png'),
                   'favicon': '{}{}'.format(settings.STATIC_URL, 'site/favicon.ico'),
                   }
        html = template.render(context, request)
        return html


class bill_sale_interstate(View):
    def get(self, request, *args, **kwargs):
        if request.method == 'GET' :
            customer = Customers.objects.only('idcustomer', 'cusname').get(pk=kwargs['customer_id'])
            units = Units.objects.filter(idcustomer=kwargs['customer_id'], status='Active')
            return render(request, 'Procedure/Customers/Applications/OTHER/mcd_356_texas.html',
                          {'customer': customer, 'units': units})


@login_required(login_url='Procedure:login')
def small_corp(request, customer_id):
    if request.method == 'GET':
        customer = Customers.objects.only('idcustomer', 'cusname').get(pk=customer_id)
        return render(request, 'Procedure/Customers/Applications/OTHER/small-corp.html',
                      {'customer': customer})
    if request.method == 'POST':
        customer = Customers.objects.get(idcustomer=customer_id)
        state = States.objects.only('state', 'codestate').get(codestate=customer.state)
        date = datetime.today().strftime('%m/%d/%Y')
        data = {
            'FEIN': customer.fein,
            'NAME CORP': customer.cusname,
            'ADDRESS': customer.address, 'CITY': customer.city,
            'STATE': state.codestate + ' ' + customer.codepostal,
            'TELEPHONE': customer.mobile1 if customer.mobile1 else '',
            'DATE': date, 'OWNER': customer.owner + ' ' + customer.owner_surname,
            'NAME ADDRESS': customer.owner + ' ' + customer.owner_surname + '\n' + customer.address + '\n' + customer.city + ' ' + customer.state + ' ' + customer.codepostal,
            'SSN': customer.ssn, 'DATE INCORPORATED': request.POST.get('date_incorporated')
        }
        if customer.corptype == 'INC' or customer.corptype == 'CORP':
            data['TITLE'] = 'PRESIDENT'
        elif customer.corptype == 'LLC':
            data['TITLE'] = 'AMBR'
        else:
            data['TITLE'] = '?'

        file_name = 'small-corp%s.pdf' % customer_id
        generate_pdf_fill('OTHER/SMALLCORPf2553.pdf', data, file_name)
        return JsonResponse({'filename': file_name})