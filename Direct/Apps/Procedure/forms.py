import datetime
from django import forms

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import Textarea, Select, DateInput, TextInput, EmailInput, RadioSelect, NumberInput, CheckboxInput, \
    FileInput
from django.forms.models import inlineformset_factory
from django.template.loader_tags import register

from .models import Customers, States, Units, Invoices, Invoice_det, Services, Invoice_paid, Millages, Recive, Drivers, \
    Exams, Notes, Cards, User, NotesProjects, RandomTest, Road_Taxes, Customer_Files
from .select_choices import corptype_choices, languages_choices, delivery, client_type, annual_report_choices, \
    florida_tag


class CustomersForm(forms.ModelForm):
    corptype = corptype_choices()
    language = languages_choices()
    method = delivery()
    floridaid = client_type()

    class Meta:
        model = Customers
        m = States
        widgets = {'since': DateInput(format="%m/%d/%Y", attrs={'class': 'datepicker form-control form-control-sm',
                                                                'value': datetime.datetime.today().strftime(
                                                                    '%m/%d/%Y')}),
                   'clientpass': Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control form-control-sm'}),
                   'cusname': TextInput(attrs={'class': 'form-control'}),
                   'floridaid': Select(attrs={'class': 'form-select form-select-sm', 'required': 'required'}),
                   'floridaexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'mcexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'owner': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'First Name'}),
                   'owner_surname': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'Last Name'}),
                   'anreport': Select(choices=annual_report_choices(), attrs={'class': 'validate_annual_report selectize'}),
                   'dotidexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'dot_lease': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'bitexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'irpexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'caexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'campcexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'mnexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'nyexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'californiaexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'explic': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'iftaexp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'insuexpire': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'contact1': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'contact2': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'email': EmailInput(attrs={'class': 'form-control form-control-sm'}),
                   'address': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'kyuid': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'mn': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'orid': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'mcreg': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'referred': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'careg': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'california': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'statecorp': Select(choices=States.objects.all().values_list('state', 'state'),
                                       attrs={'class': 'form-control form-control-sm'}),
                   'statelic': Select(choices=States.objects.all().values_list('codestate', 'codestate')),
                   'clientstatus': RadioSelect(choices=(('Active', 'Active'), ('Inactive', 'Inactive'))),
                   'iftastate': Select(choices=States.objects.all().values_list('codestate', 'codestate')),
                   'state_permits': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'state_permits_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'city_license': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'city_license_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'county_license': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'county_license_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'new_jersey': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'new_jersey_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'over_size_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'over_weight_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'inner_bridge_exp': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'dot_biennal_update': TextInput(attrs={'class': 'form-control form-control-sm'}),
                   'dot_biennal_update_date': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
                   'state': Select(choices=States.objects.all().values_list('codestate', 'state'),
                                   attrs={'class': 'form-control form-control-sm'}),
                   'dot_user_clearinghouse': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'User Clearinghouse'}),
                   'dot_password_clearinghouse': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'Password Clearinghouse'}),
                   'dot_note_clearinghouse': Textarea(
                       attrs={'rows': '4', 'cols': '40', 'class': 'form-control form-control-sm',
                              'placeholder': 'Notes Clearinghouse'}),
                   'dotclient': CheckboxInput(attrs={'class': 'form-check-input'}),
                   'test': CheckboxInput(attrs={'class': 'form-check-input'}),
                   'irp_taxid': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'IRP TAXID'}),
                   'irp_dot': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'IRP DOT'}),
                   'annual_inspection_truck': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'Annual Inspection Truck'}),
                   'annual_inspection_truck_expiration': DateInput(
                       attrs={'class': 'datepicker form-control form-control-sm'}),
                   'annual_inspection_trailer': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'Annual Inspection Trailer'}),
                   'annual_inspection_trailer_expiration': DateInput(
                       attrs={'class': 'datepicker form-control form-control-sm'}), 'fmcsa_user': TextInput(
                attrs={'class': 'form-control form-control-sm', 'placeholder': 'FMCSA USER'}),
                   'fmcsa_password': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'FMCSA PASSWORD'}),
                   'ny_tax_user': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'NY USER'}),
                   'ny_tax_password': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'NY PASSWORD'}),
                   'prepass': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'USERNAME'}),
                   'prepass_password': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'PASSWORD'}),
                   'random_test_note': Textarea(attrs={'rows': 3, 'cols': 40, 'class': 'form-control form-control-sm',
                                                       'placeholder': 'Random Test Note'}),
                   'medical_card_expiration_date': DateInput(
                       attrs={'class': 'datepicker form-control form-control-sm'}),
                   'fuel_taxes': CheckboxInput(attrs={'class': 'form-check-input', 'hidden': 'hidden'}),
                   'iftaid': TextInput(attrs={'class': 'form-control-sm ifta'}),
                   'userid': TextInput(attrs={'class': 'form-control form-control-sm ifta'}),
                   'passuserid': TextInput(attrs={'class': 'form-control form-control-sm ifta'}),
                   'ct_user': TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'CT USER'}),
                   'ct_password': TextInput(
                       attrs={'class': 'form-control form-control-sm', 'placeholder': 'CT PASSWORD'}),
                   'BOIR': CheckboxInput(attrs={'class': 'form-check-input'})
                   }
        fields = '__all__'


@register.filter(is_safe=True)
def label_with_classes(value, arg):
    return value.label_tag(attrs={'class': arg})


class UnitForm(forms.ModelForm):
    class Meta:
        model = Units
        widgets = {
            'nounit': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'irp': TextInput(attrs={'class': 'form-control form-control-sm noSpecialCharacters'}),
            'road_taxes_date': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
            'road_taxes': Select(attrs={'class': 'form-control'}),
            'year': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'make': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'type': Select(attrs={'class': 'form-control form-control-sm'}),
            'vin': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'title': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'state': Select(choices=States.objects.all().values_list('codestate', 'codestate'),
                            attrs={'class': 'form-control form-control-sm'}),
            'fuel': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'gross': TextInput(attrs={'class': 'form-control form-control-sm onlyNumbers'}),
            'empty': TextInput(attrs={'class': 'form-control form-control-sm onlyNumbers'}),
            'color': TextInput(attrs={'class': 'form-control form-control-sm'}),
            'date': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
            'price': TextInput(
                attrs={'type': 'number', 'step': 'any', 'min': '0',
                       'class': 'form-control form-control-sm onlyDecimals'}),
            'expiration_date': DateInput(attrs={'class': 'datepicker form-control form-control-sm'}),
            'lease': CheckboxInput(attrs={'class': 'form-check-input'}),
            'ifta': CheckboxInput(attrs={'class': 'form-check-input'})
        }
        fields = [
            'idcustomer', 'idfueltax', 'nounit', 'irp', 'road_taxes_date', 'road_taxes', 'year', 'make', 'type', 'vin',
            'title', 'state', 'fuel', 'gross', 'empty', 'color', 'date', 'price', 'status', 'expiration_date', 'lease', 'ifta'
        ]

    def clean(self):
        super(UnitForm, self).clean()
        irp = self.cleaned_data.get('irp')
        make = self.cleaned_data.get('make')
        if irp and len(irp) < 3:
            self._errors['irp'] = self.error_class(['Minimum 3 characteres required'])
        if make and len(make) < 2:
            self._errors['make'] = self.error_class(['Minimum 2 characteres required'])

        return self.cleaned_data


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoices
        widgets = {
            "invdate": DateInput(
                attrs={"class": "form-control datepicker", "value": datetime.datetime.today().strftime("%m/%d/%Y")}),
            "coments": Textarea(attrs={"class": "form-control", "rows": "2"}),
            "amount": NumberInput(attrs={"class": "form-control form-control-sm", "readonly": "True"}),
            "deu": NumberInput(attrs={"class": "form-control form-control-sm", "readonly": "True"})
        }
        fields = "__all__"

    def customSave(self, user, deu):
        invoice = self.save(commit=False)
        invoice.iduser = User.objects.get(pk=user)
        invoice.deu = deu
        invoice.save()
        return invoice


class InvoiceDetForm(forms.ModelForm):
    class Meta:
        model = Invoice_det
        choices = list()
        choices.append(('0', '--select--'))
        for s in Services.objects.filter(is_active=True):
            choices.append((s.description, "{0} {1}".format(s.idservice, s.description)))
        widgets = {
            "code": NumberInput(attrs={'class': 'code form-control', 'readonly': 'True'}),
            "service": Select(choices=choices,
                              attrs={'class': 'services form-control', 'select': ' '}),
            "quantity": NumberInput(attrs={'class': 'qty form-control', 'required': 'true'}),
            "cost": NumberInput(attrs={'class': 'price form-control'}),
            "rate": NumberInput(attrs={'class': 'rate form-control'}),
            "discount": NumberInput(attrs={"class": "discount form-control"}),
            "discountype": Select(choices=(("", "Select"), ("$", "S"), ("%", "%")),
                                  attrs={'class': 'typediscount form-control'}),
            "amount": NumberInput(attrs={'class': 'total form-control', 'required': 'true'}),
            "coments": Textarea(
                attrs={'class': 'comment form-control no', 'rows': '1', 'cols': '30', 'required': 'true'})
        }
        fields = ["code", "service", "quantity", "cost", "rate", "discount", "discountype", "amount", "coments"]

    def clean(self):
        super(InvoiceDetForm, self).clean()
        comments = self.cleaned_data.get('coments')
        if comments and len(comments) < 3:
            self._errors['coments'] = self.error_class(['Minimum 3 characteres required'])
        # if comments.find('...') == 0:
        #    self._errors['coments'] = self.error_class(['You have to write a real comment'])
        return self.cleaned_data


class CategoryRoadTaxForm(forms.Form):
    choices = list()
    choices.append(('0', '--Select--'))
    for s in Road_Taxes.objects.all().only('id', 'category'):
        choices.append((s.id, s.category))
    category = forms.CharField(label='Category:', widget=forms.Select(choices=choices, attrs={
        'class': 'form-select form-select-sm send-query'}))
    months = forms.IntegerField(label='Months:', widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-sm send-query', 'value': '12', 'min': '1'}))
    tax_value = forms.FloatField(label='Tax Value:', widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-sm', 'readonly': 'true'}))


class FloridaTagTaxForm(forms.Form):
    classification = forms.CharField(label='Category:', widget=forms.Select(choices=florida_tag(), attrs={'class': 'form-select form-select-sm send-query'}))
    months = forms.IntegerField(label='Months:', widget=forms.NumberInput(attrs={'class':'form-control form-control-sm send-query', 'value': '12', 'min':'1'}))
    tax_value = forms.FloatField(label='Tax Value:', widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'readonly': 'true'}))


class PaidForm(forms.Form):
    fullypaid = forms.ChoiceField(choices=((1, "Yes"), (0, "No")), widget=forms.RadioSelect)
    datepaid = forms.CharField()
    paid = forms.FloatField(min_value=0)
    due = forms.FloatField(min_value=0)
    typepaid = forms.ChoiceField(
        choices=(("Cash", "Cash"), ("Credit Card", "Credit Card"), ("Check", "Check"), ("Zelle", "Zelle")))
    approved = forms.IntegerField()
    comment = forms.CharField(required=False)


class UpdatePaidFrm(forms.ModelForm):
    class Meta:
        model = Invoice_paid
        fields = "__all__"


class MillagesForm(forms.ModelForm):
    class Meta:
        model = Millages
        quarter = [[1, "1St Quarter(Jan-Mar)"], [2, "2Nd Quarter(Apr-Jun)"], [3, "3Rd Quarter(Jul-Sep)"],
                   [4, "4Th Quarter(Oct-Dec)"]]
        widgets = {
            "year": DateInput(attrs={"class": "form-control-sm yearpicker"}),
            "qtr": Select(choices=quarter, attrs={"class": "form-control-sm"}),
            "total": NumberInput(attrs={"class": "form-control-sm", "readonly": "true"})
        }
        fields = "__all__"


class ReciveForm(forms.ModelForm):
    class Meta:
        model = Recive
        quarter = [[1, "1St Quarter(Jan-Mar)"], [2, "2Nd Quarter(Apr-Jun)"], [3, "3Rd Quarter(Jul-Sep)"],
                   [4, "4Th Quarter(Oct-Dec)"]]
        widgets = {
            "idunit": Select(attrs={"class": "form-control-sm"}),
            "year": TextInput(attrs={"class": "form-control-sm yearpicker", "disabled": "true"}),
            "date": DateInput(attrs={"class": "form-control form-control-sm datepicker"}),
            "zip": TextInput(attrs={"class": "form-control form-control-sm"}),
            "quarter": Select(choices=quarter, attrs={"class": "form-select form-select-sm", "disabled": "true"}),
            "state": Select(choices=States.objects.all().values_list('codestate', 'codestate'),
                            attrs={"class": "form-select form-select-sm"}),
            "gallons": NumberInput(attrs={"class": "form-control form-control-sm"}),
            "miles": NumberInput(attrs={"class": "form-control form-control-sm"})
        }
        fields = "__all__"


class DriverForm(forms.ModelForm):
    class Meta:
        model = Drivers
        widgets = {
            "nombre": TextInput(attrs={"class": "form-control form-control-sm"}),
            "phone": TextInput(attrs={"class": "form-control form-control-sm"}),
            "ssn": TextInput(attrs={"class": "form-control form-control-sm"}),
            "cdl": TextInput(attrs={"class": "form-control form-control-sm"}),
            "cdl_state": Select(choices=States.objects.all().values_list('state', 'state'),
                                       attrs={'class': 'form-control form-control-sm'}),
            "preemp": CheckboxInput(attrs={"class": "form-check-input"}),
            "random_test": CheckboxInput(attrs={"class": "form-check-input"}),
            "status": TextInput(attrs={"class": "form-control form-control-sm"}),
            "date_of_birth": DateInput(format="%m/%d/%Y", attrs={'class': 'datepicker form-control form-control-sm'}),
            "email": EmailInput(attrs={'class': 'form-control form-control-sm'}),
            "medical_card_expiration_date": DateInput(format="%m/%d/%Y",
                                                      attrs={'class': 'datepicker form-control form-control-sm'}),
            "username_clearinghouse": TextInput(attrs={"class": "form-control form-control-sm"}),
            "password_clearinghouse": TextInput(attrs={"class": "form-control form-control-sm"}),
            "queries": NumberInput(attrs={'class': 'form-control form-control-sm'})
        }
        fields = "__all__"

    def customSave(self):
        driver = self.save(commit=False)
        driver.save()
        return driver


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exams
        typeList = [['Pre-Employment', 'Pre-Employment'], ['Random', 'Random'], ['Suspicion', 'Suspicion'],
                    ['Post Accident', 'Post Accident'], ['Return to Duty', 'Return to Duty'],
                    ['Follow Up', 'Follow Up'],
                    ['Alcohol', 'Alcohol']]
        resultList = [['Negative', 'Negative'], ['Negative Dilute', 'Negative Dilute'], ['Positive', 'Positive'], ['Rejected', 'Rejected'],
                      ['Refused', 'Refused']]
        widgets = {
            "type": Select(choices=typeList, attrs={"class": 'form-control form-control-sm'}),
            "dateexam": DateInput(attrs={"class": "form-control form-control-sm datepicker"}, format='%m/%d/%Y'),
            "result": Select(choices=resultList, attrs={"class": 'form-control form-control-sm'}),
            "dateresult": DateInput(attrs={"class": "form-control form-control-sm datepicker"}, format='%m/%d/%Y'),
            "lote_expiration": DateInput(attrs={"class": "form-control form-control-sm datepicker"}, format='%m/%d/%Y'),
            "lote_number": TextInput(attrs={"class": "form-control form-control-sm"}),
            "path": FileInput(attrs={"class": "form-control form-control-sm"})
        }
        fields = "__all__"


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        widgets = {
            'created_at': DateInput(
                attrs={'class': 'form-control form-control-sm datepicker'}, format='%m/%d/%Y'),
            'note': Textarea(attrs={'rows': 2, 'cols': 20, 'class': 'form-control form-control-sm'}),
            'status': TextInput(attrs={'hidden': 'true', 'value': 'Active'})
        }
        fields = '__all__'


class RandomTestForm(forms.ModelForm):
    class Meta:
        model = RandomTest
        fields = '__all__'


class CardsForm(forms.ModelForm):
    class Meta:
        model = Cards
        fields = '__all__'
        exclude = {'last_used', 'status'}


class CustomUserCreationForm(UserCreationForm):
    change_password = forms.BooleanField(initial=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'change_password')


class CustomUserChangeForm(UserChangeForm):
    change_password = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'change_password')


class UploadReceipts(forms.Form):
    quarter = [[1, "1St Quarter(Jan-Mar)"], [2, "2Nd Quarter(Apr-Jun)"], [3, "3Rd Quarter(Jul-Sep)"],
               [4, "4Th Quarter(Oct-Dec)"]]
    idunit = forms.CharField()
    year = forms.CharField(max_length=4,
                           widget=forms.TextInput(attrs={'class': 'form-control-sm yearpicker', 'disabled': 'true'}))
    quarter = forms.CharField(max_length=4, widget=forms.Select(choices=quarter,
                                                                attrs={'class': 'form-select-sm', 'disabled': 'true'}))
    excel_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'title': 'Upload excel File', 'required': 'required'}))


class NotesProjectsForm(forms.ModelForm):
    class Meta:
        model = NotesProjects
        fields = "__all__"


class CustomerFilesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Customer_Files
        fields = "__all__"


class FilesUploadForm(forms.Form):
    filename = forms.CharField()
    folder = forms.CharField()
    path = forms.FileField()


InvoicesDetFormSet = inlineformset_factory(Invoices, Invoice_det, form=InvoiceDetForm, extra=1)
# InvoicesDetFormSet = formset_factory(InvoiceDetForm, extra=1)


class TaskForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm text-black', 'required': 'True', 'required': 'required'}))
    priority = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control form-control-sm text-black'}), required=False)
    users = list()
    users.append(('0', '--Select--'))
    for user in User.objects.filter(is_active=True):
        users.append((user.id, user.fullname))
    due_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control datepicker text-black', 'required': 'False'}))
    to_assign = forms.ChoiceField(choices=users, required=False)


class ProjectsForm(forms.Form):
    customers = list()
    customers.append(('', '------- Select ---------'))
    for customer in Customers.objects.filter(clientstatus='Active').only('idcustomer', 'cusname'):
        customers.append((customer.idcustomer,'{0}-{1}'.format(customer.idcustomer, customer.cusname)))
    services = list()
    services.append(('', '-------- Select ---------'))
    for service in Services.objects.filter(is_active=True, is_project=True, need_invoice=False):
        services.append((service.idservice,service.description))
    customer = forms.ChoiceField(choices=customers, widget=forms.Select(attrs={'class': 'form-select form-select-lg selectize'}))
    service = forms.ChoiceField(choices=services, widget=forms.Select(attrs={'class': 'form-select form-select-lg selectize'}))
    #service_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'type': 'number'}))
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control form-control-sm', 'cols': 40, 'rows': 2}))
