import random
import json
import math
from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models import Q

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from .models import Detail_RandomList, RandomList
from ..Procedure.models import Customers, Drivers, Notes
from ..helpers.message import MessageResponse


@login_required(login_url='Procedure:login')
def consortium(request):
    content_type = ContentType.objects.get_for_model(Drivers)
    Permission.objects.get_or_create(
        name="Drivers Report",
        codename="drivers_report",
        content_type=content_type,
    )
    today = datetime.today().strftime("%Y-%m-%d")
    query = "SELECT c.idcustomer, c.cusname, c.dotclient, c.clientstatus, d.nombre, d.status, d.nombre, d.phone, CONCAT_WS('','***-**-', SUBSTRING(d.ssn, 8, 10)) AS ssn_k FROM customers c LEFT JOIN drivers d ON c.idcustomer=d.idcustomer WHERE (c.clientstatus='Active' AND c.dotclient=True AND c.bitexp>='{0}' AND d.status='Active' AND d.random_test=true) OR (c.clientstatus='Active' AND c.dotclient=True AND c.bitexp>='{0}' AND d.random_test IS NULL) ORDER BY c.idcustomer DESC ;".format(today)
    drivers = Customers.objects.raw(query)
    num = len(drivers)
    return render(request, 'Consortium/consortium.html', {'drivers': drivers, 'num_rows': num})


class RandomListView(View):
    def get(self, request, *args, **kwargs):
        try:
            year = datetime.today().year if request.GET.get('year') is None else int(request.GET.get('year'))
            quarter = self.get_quarter(datetime.today()) if request.GET.get('quarter') is None else int(request.GET.get('quarter'))
            drivers_tests = drivers_random_test_program()
            count_drivers = len(drivers_tests)            
            quarters = [
                {'item': 1, 'name': '1st Quarter(Jan-Mar)'},
                {'item': 2, 'name': '2nd Quarter(Apr-Jun)'},
                {'item': 3, 'name': '3rd Quarter(Jul-Sep)'},
                {'item': 4, 'name': '4th Quarter(Oct-Dec)'}
            ]
            details_random_list = Detail_RandomList.objects.filter(random_list__year=year)
            current_alcohol_test = details_random_list.filter(test_alcohol=True, test_file__isnull=False)
            current_drugs_test = details_random_list.filter(test_substances=True, test_file__isnull=False)
            random_list =RandomList.objects.filter(year=year, quarter=quarter).first()          
            total_selected =details_random_list.filter(random_list__quarter=quarter).count()
            if kwargs.get('table') == 1:
                filtered_alcohol_test = details_random_list.filter(test_alcohol=True, random_list__quarter=quarter)
                filtered_drugs_test = details_random_list.filter(test_substances=True, random_list__quarter=quarter)                
                data = {
                    'filtered_alcohol': {
                        "total": filtered_alcohol_test.count(),
                        "completed": filtered_alcohol_test.filter(test_file__isnull=False).count(),
                        "percentage": round((filtered_alcohol_test.filter(test_file__isnull=False).count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    },
                    'filtered_drugs': {
                        "total": filtered_drugs_test.count(),
                        "completed": filtered_drugs_test.filter(test_file__isnull=False).count(),
                        "percentage": round((filtered_drugs_test.filter(test_file__isnull=False).count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    },
                    'current_alcohol': {
                        "number": current_alcohol_test.count(),
                        "percentage": round((current_alcohol_test.count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    },
                    'current_drugs': {
                        "number": current_drugs_test.count(),
                        "percentage": round((current_drugs_test.count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    },
                    'total_selected': total_selected,
                }
                if total_selected != 0:
                    data['show'] = random_list.show
                    data['random_list_id'] = random_list.id
                return JsonResponse(data, safe=False)
            else:
                data = {
                    'quarter_selected': quarter,
                    'quarters': quarters,
                    'total_drivers': count_drivers,               
                    'current_alcohol': {
                        "number": current_alcohol_test.count(),
                        "percentage": round((current_alcohol_test.count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    },
                    'current_drugs': {
                        "number": current_drugs_test.count(),
                        "percentage": round((current_drugs_test.count() * 100) / count_drivers, 2) if count_drivers != 0 else 0
                    }, 
                    'total_selected': total_selected
                }
                if total_selected != 0:
                    data['show'] = random_list.show
                    data['random_list_id'] = random_list.id
                return render(request, 'Consortium/random.html', data)
        except Exception as e:
          print('An exception occurred', e)
          return MessageResponse(description='Error while get random list').error()
    
    def post(self, request, *args, **kwargs):
        try:             
            year = request.POST.get('year')            
            quarter = int(request.POST.get('quarter'))
            return self.generateRandomList(request, year, quarter)
        except Exception as e:
            print(e)
            return MessageResponse(description='Error while get random list').error()
    
    def patch(self, request, *args, **kwargs):
        try:
            params = json.loads(request.body)
            RandomList.objects.filter(id=params['id']).update(show=params['show'])
            return MessageResponse(description='Updated successfully').success()
        except Exception as e:
            print(e)
            return MessageResponse(description='Internal Server Error').error()
    
    def generateRandomList(self, request, year, quarter): 
        today = datetime.today().strftime("%Y-%m-%d")
        Customers.objects.filter(dotclient=True, bitexp__lte=today).update(dotclient=False)          
        
        random_drug_testing_rate = 50 / 100
        random_alcohol_testing_rate = 10 / 100
        try:
            drivers_tests = drivers_random_test_program()
            count_drivers = len(drivers_tests)
            #Drivers selected Drugs Test
            percentage = random_drug_testing_rate / 4
            tests_drugs = round(count_drivers * percentage)
            if quarter == 4:
                current_tests = Detail_RandomList.objects.filter(random_list__year=year, test_substances=True, status='Completed').count()
                tests_drugs = math.ceil(count_drivers * random_drug_testing_rate) - current_tests
            selected_drugs = random.sample(list(drivers_tests), tests_drugs)
            #Drivers selected Alcohol Test
            percentage = random_alcohol_testing_rate / 4
            tests_alcohol = round(count_drivers * percentage)
            if quarter == 4:
                current_tests = Detail_RandomList.objects.filter(random_list__year=year, test_alcohol=True, status='Completed').count()
                tests_alcohol = math.ceil(count_drivers * random_alcohol_testing_rate) - current_tests
            selected_alcohol = random.sample(list(drivers_tests), tests_alcohol)  
            random_list = ClassifyTest(selected_drugs, selected_alcohol)
            header_random_list = RandomList(
                created_by=request.user,
                current_drivers=count_drivers,
                year=year,
                quarter=quarter,
                drug_testing_rate=random_drug_testing_rate,
                alcohol_testing_rate=random_alcohol_testing_rate
            )
            header_random_list.save()
            SaveAndNotifyRandomTest(random_list, header_random_list, request.user)
            message = {'description': 'New Random add', 'type': 'success'}
            result = JsonResponse({'message': message})
            status = 200
        except Exception as e:
            print(e)
            message = {'description': 'Error when generate Random pool', 'type': 'error'}
            result = JsonResponse({'message': message})
            status = 500
        return HttpResponse(result, content_type='application/json', status=status)

    
    def get_quarter(self, var_date):
        month = var_date.month
        return (month -1) // 3 + 1
        
    
def drivers_random_test_program():
    today = datetime.today()
    drivers_tests = Customers.objects.filter(
                Q(clientstatus='Active', dotclient=True, bitexp__gte=today, drivers__status='Active', drivers__random_test=True) |
                Q(clientstatus='Active', dotclient=True, bitexp__gte=today, drivers__random_test__isnull=True)
            ).order_by('-idcustomer').prefetch_related('drivers').values('idcustomer', 'drivers__iddriver')
    return drivers_tests


def SaveAndNotifyRandomTest(list_random, header_random_list, user):
    current_date = datetime.now()
    expiration_date = current_date + timedelta(days=7)
    fullname = user.fullname
    for customer_id, values in list_random.items():
        message = "Drivers seleccionados para random test: "
        try:
            if isinstance(values, dict) and ("Substances" not in values.keys()) and ("Alcohol" not in values.keys()):
                selected_drivers = message
                for driver, tests in values.items():
                    drug_test = True if "Substances" in tests.keys() else False
                    alcohol_test = True if "Alcohol" in tests.keys() else False
                    detail = Detail_RandomList(
                        random_list = header_random_list,
                        customer_id = customer_id,
                        driver_id = driver,
                        test_substances = drug_test,
                        test_alcohol = alcohol_test,
                    )
                    detail.save()
                    drivers_model = Drivers.objects.only('nombre').get(iddriver=driver)
                    selected_drivers += "{0} para {1} \n".format(drivers_model.nombre.title(), SelectTest(tests).lower())
                new_note = Notes(
                    idcustomer_id=customer_id,
                    fullname=fullname,
                    created_at=current_date,
                    date_expiry=expiration_date,
                    note=selected_drivers,
                    iduser=user
                )
                new_note.save()                
            else:
                drug_test = True if "Substances" in values.keys() else False
                alcohol_test = True if "Alcohol" in values.keys() else False
                detail = Detail_RandomList(
                    random_list = header_random_list,
                    customer_id=customer_id,
                    test_substances=drug_test,
                    test_alcohol=alcohol_test
                )
                detail.save()
                message = "Seleccionado en random test para {0} ".format(SelectTest(values))
                new_note = Notes(
                    idcustomer_id=customer_id,
                    fullname=fullname,
                    created_at=current_date,
                    date_expiry=expiration_date,
                    note=message,
                    iduser=user
                )
                new_note.save()
        except Exception as e:
            print(e)


def SelectTest(selected_test):
    tests = selected_test.keys()
    substances = True if "Substances" in tests else False
    alcohol = True if "Alcohol" in tests else False
    if substances and alcohol:
        return "Sustancias y Alcohol"
    if substances:
        return "Sustancias"
    if alcohol:
        return "Alcohol"


def ClassifyTest(substances_tests, alcohol_tests):
    substances_tests = sorted(substances_tests, key=lambda x: x["idcustomer"])
    alcohol_tests = sorted(alcohol_tests, key=lambda x: x["idcustomer"])
    grouped_tests = {}
    try:
        for test in substances_tests:
            idcustomer = test['idcustomer']
            iddriver = test['drivers__iddriver'] if test['drivers__iddriver'] else None
            if idcustomer in grouped_tests:
                grouped_tests[idcustomer][iddriver] = {'Substances': True}
            else:
                if iddriver:
                    grouped_tests[idcustomer] = {}
                    grouped_tests[idcustomer][iddriver] = {'Substances': True}
                else:
                    grouped_tests[idcustomer] = {'Substances': True}

        for test in alcohol_tests:
            customer_id = test['idcustomer']
            driver_id = test['drivers__iddriver'] if test['drivers__iddriver'] else None
            if customer_id in grouped_tests:
                if driver_id:
                    grouped_tests[customer_id][driver_id] = {'Substances': True, 'Alcohol': True}
                else:
                    grouped_tests[customer_id] = {'Substances': True, 'Alcohol': True}
            else:
                if driver_id:
                    grouped_tests[customer_id] = {}
                    grouped_tests[customer_id][driver_id] = {'Alcohol': True}
                else:
                    grouped_tests[customer_id] = {'Alcohol': True}
    except Exception as e:
        print("Error Generate Notification %s" % e)
    return grouped_tests
