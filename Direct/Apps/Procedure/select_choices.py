import datetime

from django import forms
from django.db.models import Value, CharField
from django.db.models.functions import Concat

from .models import User, Customers, Services, States, Road_Taxes, Florida_Tag


def customers_choices():
    customers_list = [('--Select--', '--Select--')]
    customers_list.extend(
        Customers.objects.filter(clientstatus='Active')
        .annotate(cusname_select=Concat('idcustomer', Value('-'), 'cusname', output_field=CharField())).
        values_list('idcustomer', 'cusname_select')
    )
    return field_select(customers_list, 'Customers', class_names='form-select form-select-lg selectize')


def annual_report_choices():
    choices = (('', '--Select--'), ('N/A', 'N/A'), ('INACTIVE', 'INACTIVE'),
               (datetime.date.today().year + 1, datetime.date.today().year + 1),
               (datetime.date.today().year, datetime.date.today().year),
               (datetime.date.today().year - 1, datetime.date.today().year - 1)
               )
    return choices


def status_choices():
    choices = (('Active', 'Active'), ('Inactive', 'Inactive'))
    return choices


def users_choices(label='Users', field=True):
    users_list = [(0, '---Select--')]
    users_list.extend(
        User.objects.only('id', 'fullname').filter(is_active=True).exclude(id=40).values_list('id', 'fullname'))
    if not field:
        return users_list
    return field_select(users_list, label)


def services_choices(*args, field=True, is_project=False):
    services_list = [(0, '--Select---')]
    services = Services.objects.filter(is_active=True)
    if is_project:
        services = services.filter(is_project=True, need_invoice=False)
    services_list.extend(
        services
        .annotate(list_new=Concat('idservice', Value('-'), 'description', output_field=CharField()))
        .values_list(*args))
    if field:
        return field_select(services_list, 'Services')
    else:
        return services_list


def states_choices(*fields):
    states = States.objects.all().values_list(*fields)
    return states


def corptype_choices():
    choices = (('0', '------'), ('CORP', 'CORP'), ('FICTITIOUS', 'FICTITIOUS'), ('INC', 'INC'), ('LLC', 'LLC'),  ('S-CORP', 'S-CORP'), ('S-PROPIETOR SHIP', 'S-PROPIETOR SHIP'))
    return field_select(choices, 'Corp Type')


def languages_choices():
    choices = (('', '--------'), ('English', 'English'), ('Spanish', 'Spanish'))
    return field_select(choices, 'Languages')


def delivery():
    choices = (('0', '--------'), ('UPS', 'UPS'), ('FEDEX', 'FEDEX'), ('Regular Mail', 'Regular Mail'))
    return field_select(choices, 'Delivery Method')


def client_type():
    choices = (
        ('', '--------'), ('Local', 'Local'), ('Auto', 'Auto'), ('Inter-State', 'Inter-State'), ('Taxes', 'Taxes'))
    return field_select(choices, 'Client Type')


def units_type_choices():
    return ('', '--------'), ('DP', 'DUMP TRUCK'), ('TK', 'TRUCK'), ('TR', 'TRACTOR'), ('TL', 'TRAILER'), ('TT', 'TOWING'),('BS', 'BUS'), ('AUTO', 'AUTO'), ('VESSEL', 'VESSEL')


def road_taxes_choices():
    choices = [(0, '---Select---')]
    choices.extend(Road_Taxes.objects.all().values_list('id', 'category'))
    return choices


def florida_tag():
    choices = [(0,'---Select---')]
    choices.extend(Florida_Tag.objects.all().values_list('id', 'classification_gvw'))
    return choices


def quarter_choices():
    return [[1, "1St Quarter(Jan-Mar)"], [2, "2Nd Quarter(Apr-Jun)"], [3, "3Rd Quarter(Jul-Sep)"],
            [4, "4Th Quarter(Oct-Dec)"]]


def paid_choices():
    return ("Cash", "Cash"), ("Credit Card", "Credit Card"), ("Check", "Check"), ("Credit", "Credit")


def yes_no_options():
    return (1, "Yes"), (0, "No")


def exams_type():
    return [['Pre-Employment', 'Pre-Employment'], ['Random', 'Random'], ['Suspicion', 'Suspicion'],
            ['Post Accident', 'Post Accident'], ['Return to Duty', 'Return to Duty'], ['Follow Up', 'Follow Up'],
            ['Alcohol', 'Alcohol']]


def exams_result():
    return [['Negative', 'Negative'], ['Positive', 'Positive'], ['Rejected', 'Rejected'], ['Refused', 'Refused']]


# Return select field
def field_select(choices, text='', class_names='form-select form-select-sm'):
    return forms.ChoiceField(
        label=text,
        choices=choices, initial=0,
        widget=forms.Select(attrs={'class': class_names, 'placeholder': '-----Select----'})
    )
