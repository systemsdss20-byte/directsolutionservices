from datetime import datetime

from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import FileExtensionValidator
from django.db import models
from encrypted_fields import fields
from simple_history.models import HistoricalRecords


def users_directory(instance, avatar):
    return 'users/{0}/{1}'.format(instance.pk, avatar)


class User(AbstractUser):
    fullname = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    change_password = models.BooleanField(default=True, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=users_directory)
    history = HistoricalRecords()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'


class States(models.Model):
    idstate = models.BigAutoField(primary_key=True)
    codestate = models.CharField("Code State", max_length=2)
    state = models.CharField('State', max_length=60)
    history = HistoricalRecords()
    class Meta:
        db_table = 'states'

    def __str__(self):
        return '{0} {1}'.format(self.codestate, self.state)


class Services(models.Model):
    
    class RenewalFrequency(models.TextChoices):
        MONTHLY = 'Monthly', 'Monthly'
        YEARLY = 'Yearly', 'Yearly'
        NONE = 'None', 'None'
    class ExpirationType(models.TextChoices):
        INTERNAL = 'Internal', 'Internal Calculation'
        EXTERNAL = 'External', 'External Authority'
        NONE = 'None', 'No Expiration'
        
    idservice = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    rate = models.FloatField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    is_project = models.BooleanField(default=True)
    need_invoice = models.BooleanField(default=True)
    is_for_unit = models.BooleanField(default=False)
    should_notify_client = models.BooleanField(default=False)
    renewal_frequency = models.CharField(
        max_length=10,
        choices=RenewalFrequency.choices,
        default=RenewalFrequency.NONE
    )
    expiration_type = models.CharField(
        max_length=10,
        choices=ExpirationType.choices,
        default=ExpirationType.NONE
    )

    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'services'

    def __str__(self):
        return '%s %s' % (self.idservice, self.description)


Group.add_to_class('service', models.ManyToManyField(Services, verbose_name='services', blank=True, ))


class Customers(models.Model):
    idcustomer = models.BigAutoField(primary_key=True)
    since = models.DateField('Client Since', blank=False)
    anreport = models.CharField('Annual Reports', max_length=8, default='')
    cusname = models.CharField('Customer Name', max_length=200, null=False, blank=False, unique=True)
    ssn = models.CharField('SSN#', max_length=15, null=True, blank=True)
    fein = models.CharField('FEIN#', max_length=15, null=True, blank=True)
    opercomp = models.CharField('Operating Comp', max_length=200, null=True, blank=True)
    list_owner = (('LLC', 'LLC'), ('INC', 'INC'), ('CORP', 'CORP'), ('S-CORP', 'S-CORP'))
    owner = models.CharField("First Name", max_length=200, null=False, blank=False)
    owner_surname = models.CharField("Last Name", max_length=200, null=False, blank=False, default='')
    corptype = models.CharField('Corp Type', max_length=100, null=True, blank=True)
    statecorp = models.CharField('State', max_length=45, null=True, blank=True)
    corpno = models.CharField('Corp Entity No', max_length=45, null=True, blank=True)
    contact1 = models.CharField('Name Contact 1', max_length=45, null=False, blank=False)
    contact2 = models.CharField('Name Contact 2', max_length=45, null=True, blank=True)
    email = models.EmailField('E-Mail', max_length=45, null=False, blank=False)
    languages = (('English', 'English'), ('Spanish', 'Spanish'))
    language = models.CharField('Language', max_length=45, choices=languages, null=True, blank=True)
    mobile1 = models.CharField('Mobile Contact 1', max_length=45, null=False, blank=False)
    home = models.CharField('Home/Office', max_length=45, null=True, blank=True)
    mobile2 = models.CharField('Mobile Contact 2', max_length=45, null=True, blank=True)
    fax = models.CharField('Fax', max_length=45, null=True, blank=True)
    address = models.CharField('Address', max_length=200, null=False, blank=False)
    city = models.CharField('City', max_length=45, null=False, blank=False)
    state = models.CharField('State', max_length=45, null=False, blank=False)
    codepostal = models.CharField('Postal Code', max_length=8, null=False, blank=False)
    county = models.CharField('County', max_length=100, null=True, blank=True)
    method = models.CharField('Delivery Method', max_length=45, null=True, blank=True)
    acct = models.CharField('Acct', max_length=45, null=True, blank=True)
    lic = models.CharField('Driver License', max_length=45, null=True, blank=True)
    statelic = models.CharField('State', max_length=4, null=True, blank=True)
    explic = models.DateField('Owner DOB', blank=True, default='0001-01-01')
    insuexpire = models.DateField('Insurance Exp', blank=True, default='0001-01-01')
    clientstatus = models.CharField('Client Status', max_length=10, default='Active')

    dotclient = models.BooleanField('Random Test', null=True, blank=True)
    # credithold  models.CharField('Credit Hold', max_length=3, null=True, blank=True)
    credithold = models.BooleanField('Credit Hold', default=False)
    clientpass = models.CharField('Client Notes', max_length=300, null=True, blank=True, default='')
    mc = models.CharField('MC#/ UCR Year', max_length=20, null=True, blank=True)
    mcexp = models.DateField('MC#/ UCR Year', blank=True, default='0001-01-01')
    mcreg = models.CharField('Over size', max_length=20, null=True, blank=True)
    dotid = models.CharField('DOT ID # / PIN', max_length=20, null=True, blank=True)
    dotidexp = models.DateField('DOT ID#/ PIN', blank=True, default='0001-01-01')
    dotpin = models.CharField('DOT ID#/ PIN', max_length=20, null=True, blank=True)
    dot_lease = models.CharField('DOT Lease', max_length=20, null=True, blank=True)
    irpid = models.CharField('IRP ID / PIN', max_length=20, null=True, blank=True)
    irppin = models.CharField('IRP ID / PIN', max_length=20, null=True, blank=True)
    irpexp = models.DateField('IRP ID / PIN', blank=True, default='0001-01-01')
    floridaid = models.CharField('Client Type', max_length=20, null=False, blank=False, default='--Select--')
    iftaid = models.CharField('IFTA ID/ State', max_length=20, null=True, blank=True)
    iftastate = models.CharField('IFTA ID/ State', max_length=20, null=True, blank=True)
    iftaexp = models.DateField('IFTA ID/ State', blank=True, default='0001-01-01')
    iftareg = models.CharField('IFTA ID/ State', max_length=20, null=True, blank=True)
    kyuid = models.CharField('KYU ID#', max_length=20, null=True, blank=True)
    kyureg = models.CharField('KYU ID#', max_length=20, null=True, blank=True)
    mn = models.CharField('NM/ MTD/ WDT', max_length=20, null=True, blank=True)
    mnexp = models.DateField('NM/ MTD/ WDT', blank=True, default='0001-01-01')
    mnreg = models.CharField('NM/ MTD/ WDT', max_length=20, null=True, blank=True)
    nyid = models.CharField('NY ID/ PIN ', max_length=20, null=True, blank=True)
    nypin = models.CharField('NY ID/ PIN ', max_length=20, null=True, blank=True)
    nyexp = models.DateField('NY ID/ PIN', blank=True, default='0001-01-01')
    nyreg = models.CharField('NY ID/ PIN', max_length=20, null=True, blank=True)
    orid = models.CharField('OR ID', max_length=20, null=True, blank=True)
    california = models.CharField('Over Weight', max_length=20, null=True, blank=True)
    californiaexp = models.DateField('CA ID#/ PIN', blank=True, default='0001-01-01')
    campc = models.CharField('CA ID#/ PIN', max_length=20, null=True, blank=True)
    campcexp = models.DateField('KYU ID#', blank=True, default='0001-01-01')
    caepn = models.CharField('CA ID#/ PIN', max_length=20, null=True, blank=True)
    capin = models.CharField('CA ID#/ PIN', max_length=20, null=True, blank=True)
    caexp = models.DateField('CA ID#/ PIN', blank=True, null=True)
    careg = models.CharField('Inner Bridge', max_length=20, null=True, blank=True)
    bit = models.CharField('OR ID#', max_length=20, null=True, blank=True)
    bitexp = models.DateField('Random Test', blank=True, default='0001-01-01')
    boe = models.CharField('MC#/ UCR/ Year', max_length=20, null=True, blank=True)
    userid = models.CharField('State User', max_length=45, null=True, blank=True)
    passuserid = models.CharField('Password', max_length=45, null=True, blank=True)
    floridaexp = models.DateField('Client Type', blank=True, default='0001-01-01')
    overw = models.CharField('Random Test', max_length=45, null=True, blank=True)
    cusnum = models.CharField('Customer #', max_length=45, null=True, blank=True)
    prepass = models.CharField('Prepass', max_length=45, null=True, blank=True)
    prepass_password = models.CharField('Prepass', max_length=45, null=True, blank=True)
    prepassreg = models.CharField('Prepass', max_length=45, null=True, blank=True)
    referred = models.CharField('Referred By', max_length=100, null=True, blank=True)
    state_permits = models.CharField("Workers' Compensation", max_length=45, blank=True, null=True)
    state_permits_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    city_license = models.CharField('City License', max_length=45, blank=True, null=True)
    city_license_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    county_license = models.CharField('County License', max_length=45, blank=True, null=True)
    county_license_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    new_jersey = models.CharField('New Jersey', max_length=45, blank=True, null=True)
    new_jersey_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    over_weight_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    over_size_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    inner_bridge_exp = models.DateField(blank=True, null=True, default='0001-01-01')
    dot_biennal_update = models.CharField('DOT Biennal', max_length=45, blank=True, null=True)
    dot_biennal_update_date = models.DateField(blank=True, null=True, default='0001-01-01')
    dot_user_clearinghouse = models.CharField(blank=True, null=True, max_length=45)
    dot_password_clearinghouse = models.CharField(blank=True, null=True, max_length=45)
    dot_note_clearinghouse = models.CharField(blank=True, null=True, max_length=100)
    test = models.BooleanField(('Test'), blank=True, null=True, default=False)
    irp_taxid = models.CharField('IRP TAXID', blank=True, null=True, max_length=45)
    irp_dot = models.CharField('IRP DOT', blank=True, null=True, max_length=45)
    annual_inspection_truck = models.CharField('Annual Inspection Truck', blank=True, null=True, max_length=45)
    annual_inspection_truck_expiration = models.DateField(blank=True, null=True, default='0001-01-01')
    annual_inspection_trailer = models.CharField('Annual Inspection Trailer', blank=True, null=True, max_length=45)
    annual_inspection_trailer_expiration = models.DateField(blank=True, null=True, default='0001-01-01')
    fmcsa_user = models.CharField('FMCSA User', blank=True, null=True, max_length=45)
    fmcsa_password = models.CharField('FMCSA Password', blank=True, null=True, max_length=45)
    ny_tax_user = models.CharField('New York Tax', blank=True, null=True, max_length=45)
    ny_tax_password = models.CharField('New York Tax', blank=True, null=True, max_length=45)
    random_test_note = models.CharField('Random Test Note', blank=True, null=True, max_length=45)
    medical_card_expiration_date = models.DateField('Medical Card Expiration', blank=True, null=True)
    fuel_taxes = models.BooleanField(blank=True, null=True)
    ct_user = models.CharField('Connecticut', blank=True, null=True, max_length=45)
    ct_password = models.CharField(blank=True, null=True, max_length=45)
    BOIR = models.BooleanField('BOIR', default=False)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'customers'

    def __str__(self):
        return '{0}-{1}'.format(self.idcustomer, self.cusname)


class Road_Taxes(models.Model):
    category = models.CharField('Category', max_length=1)
    min_gross_weight = models.IntegerField('Min Gross Weight')
    max_gross_weight = models.IntegerField('Max Gross Weight')
    tax_value = models.DecimalField('Tax Value', decimal_places=2, max_digits=6)
    history = HistoricalRecords()
    def __str__(self):
        return '{0} (${1})'.format(self.category, self.tax_value)


class Units(models.Model):
    idunit = models.BigAutoField(primary_key=True)
    idcustomer = models.ForeignKey(Customers, models.DO_NOTHING, db_column="idcustomer")
    idfueltax = models.PositiveIntegerField(null=True, blank=True, default=1)
    nounit = models.CharField("No. Unit", max_length=15, null=False, blank=False, default='')
    irp = models.CharField("IRP ID/ PLATE", max_length=25, null=True, blank=True, default='N/A')
    road_taxes_date = models.DateField("Last Update", null=True, blank=True, default='0001-01-01')
    road_taxes = models.ForeignKey(Road_Taxes, models.DO_NOTHING, blank=True, null=True)
    year = models.CharField("Year", max_length=5)
    make = models.CharField("Make", max_length=25)
    list_type = (('AUTO', 'AUTO'), ('BS', 'BUS'), ('DP', 'DUMP TRUCK'), ('MC', 'MOTORCYCLE'), ('MH', 'MOBILE HOME'), ('PU', 'PICKUP'), ('TK', 'TRUCK'), ('TR', 'TRACTOR'), ('TL', 'TRAILER'), ('TT', 'TOWING'), ('VESSEL', 'VESSEL'))
    type = models.CharField("Type", max_length=25, choices=list_type)
    vin = models.CharField("VIN", max_length=40)
    title = models.CharField("No Title", max_length=25)
    state = models.CharField('State', max_length=4, null=True, blank=True)
    fuel = models.CharField("Fuel", max_length=10)
    gross = models.CharField("Gross Weight", max_length=25)
    empty = models.CharField("Empty Weight", max_length=25, default=0, null=True, blank=True)
    color = models.CharField("Color", max_length=10)
    date = models.DateField("Purchase Date", null=True, blank=True, default='0001-01-01')
    price = models.FloatField("Purchase Price", null=True, blank=True)
    status = models.CharField(max_length=10, null=False, blank=False, default='Active')
    expiration_date = models.DateField('Plate Expiration', null=True, blank=True, default='0001-01-01')
    lease = models.BooleanField('Lease', null=True, blank=True, default=False)
    ifta = models.BooleanField('IFTA', null=True, blank=True, default=False)
    delete = models.BooleanField(null=True, blank=True, default=False)
    history = HistoricalRecords()

    class Meta:
        db_table = 'units'

    def __str__(self):
        return '{0} {1}'.format(self.nounit, self.title)


class Invoices(models.Model):
    idinvoice = models.BigAutoField(primary_key=True)
    invdate = models.DateField("Inv Date")
    amount = models.FloatField("Amount")
    coments = models.CharField("Comments", max_length=200, null=True, blank=True)
    idcustomer = models.ForeignKey(Customers, models.DO_NOTHING, db_column="idcustomer")
    status = models.CharField("Status", max_length=10, choices=(("Unpaid", "Unpaid"), ("Paid", "Paid")))
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column="iduser")
    cusname = models.CharField("Customer", max_length=100)
    address = models.CharField("Address", max_length=200)
    paid_date = models.DateField("Date Paid", null=True, blank=True)
    deu = models.FloatField(null=True, default=0)
    deleted = models.BooleanField(default=False, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'invoices'


class Invoice_det(models.Model):
    idinvoicedet = models.BigAutoField(primary_key=True)
    idinvoice = models.ForeignKey("Invoices", models.DO_NOTHING, db_column="idinvoice", related_name='details')
    #code = models.CharField(max_length=4)
    code = models.ForeignKey('Services', models.DO_NOTHING, db_column='idservice', related_name='code')
    service = models.CharField(max_length=100)
    quantity = models.FloatField()
    rate = models.FloatField()
    discount = models.FloatField("Discount", null=True, blank=True, default=0)
    amount = models.FloatField()
    discountype = models.CharField(max_length=20, null=True, blank=True)
    coments = models.CharField('Comments', max_length=200)
    cost = models.FloatField()
    renewal_period = models.CharField(max_length=45, null=True, blank=True)
    delete = models.IntegerField(default=False, blank=True, null=True)
    history = HistoricalRecords()
    class Meta:
        db_table = "invoice_det"


class Invoice_paid(models.Model):
    idpaid = models.BigAutoField(primary_key=True)
    idinvoice = models.ForeignKey('Invoices', models.DO_NOTHING, db_column='idinvoice', related_name='paids')
    datepaid = models.DateField()
    typepaid = models.CharField(max_length=45)
    paid = models.FloatField()
    deu = models.FloatField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    iduser = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser')
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'Invoice_paid'

    def __str__(self):
        return '{0} {1}'.format('ID', self.idpaid)


class Log_Invoice_cancel(models.Model):
    # id = models.BigAutoField(primary_key=True)
    invoice_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    date_cancel = models.DateField(auto_now=True)
    motive = models.CharField(max_length=100)
    amount = models.FloatField()

    class Meta:
        managed = True
        db_table = 'log_invoice_cancel'


class Projects(models.Model):
    idproject = models.BigAutoField(primary_key=True)
    idinvoicedet = models.ForeignKey(Invoice_det, models.DO_NOTHING, db_column="idinvoicedet", null=True, blank=True)
    invoice = models.ForeignKey(Invoices, models.DO_NOTHING, null=True, blank=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.FloatField()
    service_name = models.CharField(max_length=100)
    comments = models.CharField(max_length=200)
    status = models.CharField(max_length=45)
    request = models.DateField()
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column='iduser')
    statuslast = models.DateField()
    iduserlast = models.ForeignKey(User, models.DO_NOTHING, db_column='iduserlast', related_name='iduserlast')
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='idcustomer')
    unit_id = models.ForeignKey('Units', models.DO_NOTHING, db_column='unit_id', null=True, blank=True)
    tasks_number = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    deleted = models.IntegerField(default=False, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "projects"


class NotesProjects(models.Model):
    comments = models.CharField(max_length=500)
    date_comment = models.DateTimeField(auto_now_add=True)
    date_update_comment = models.DateTimeField(null=True, blank=True)
    iduser = models.ForeignKey(User, models.DO_NOTHING)
    project = models.ForeignKey(Projects, models.DO_NOTHING)
    history = HistoricalRecords()
    

class Credits(models.Model):
    idcredit = models.BigAutoField(primary_key=True)
    # idcustomer = models.IntegerField()
    idcustomer = models.ForeignKey(Customers, models.DO_NOTHING, db_column="idcustomer")
    cusname = models.CharField(max_length=100)
    date = models.DateField()
    iduser = models.IntegerField()
    aproved = models.CharField(max_length=100, null=True, blank=True)
    credit = models.FloatField()
    comment = models.CharField(max_length=200, null=True, blank=True)
    idinvoice = models.ForeignKey(Invoices, models.DO_NOTHING, db_column="idinvoice")
    status = models.CharField(max_length=45)
    history = HistoricalRecords()

    class Meta:
        db_table = "credits"


class Millages(models.Model):
    idmillage = models.BigAutoField(primary_key=True)
    year = models.PositiveIntegerField("Year")
    qtr = models.PositiveIntegerField("Quarter")
    fl = models.FloatField("FL-Florida", blank=True, null=True)
    al = models.FloatField("AL-Alabama", blank=True, null=True)
    ak = models.FloatField("AK-Alaska", blank=True, null=True)
    ar = models.FloatField("AR-Arkanzas", blank=True, null=True)
    az = models.FloatField("AZ-Arizona", blank=True, null=True)
    ca = models.FloatField("CA-California", blank=True, null=True)
    co = models.FloatField("CO-Colorado", blank=True, null=True)
    ct = models.FloatField("CT-Connecticut", blank=True, null=True)
    dc = models.FloatField("DC-Dist. of Columbia", blank=True, null=True)
    de = models.FloatField("DE-Delaware", blank=True, null=True)
    ga = models.FloatField("GA-Georgia", blank=True, null=True)
    ia = models.FloatField("IA-Iowa", blank=True, null=True)
    id = models.FloatField("ID-Idaho", blank=True, null=True)
    il = models.FloatField("IL-Illinois", blank=True, null=True)
    in1 = models.FloatField("IN-Indiana", blank=True, null=True)
    ks = models.FloatField("KS-Kansas", blank=True, null=True)
    ky = models.FloatField("KY-Kentucky", blank=True, null=True)
    la = models.FloatField("LA-Louisiana", blank=True, null=True)
    ma = models.FloatField("MA-Massachusetts", blank=True, null=True)
    md = models.FloatField("MD-Maryland", blank=True, null=True)
    me = models.FloatField("ME-Maine", blank=True, null=True)
    mi = models.FloatField("MI-Michigan", blank=True, null=True)
    mn = models.FloatField("MN-Minnesota", blank=True, null=True)
    mo = models.FloatField("MO-Missouri", blank=True, null=True)
    ms = models.FloatField("MS-Mississippi", blank=True, null=True)
    mt = models.FloatField("MT-Montana", blank=True, null=True)
    nc = models.FloatField("NC-North Carolina", blank=True, null=True)
    nd = models.FloatField("ND-North Dakota", blank=True, null=True)
    ne = models.FloatField("NE-Nebraska", blank=True, null=True)
    nh = models.FloatField("NH-New Hampshire", blank=True, null=True)
    nj = models.FloatField("NJ-New Jersey", blank=True, null=True)
    nm = models.FloatField("NM-New Mexico", blank=True, null=True)
    nv = models.FloatField("NV-Nevada", blank=True, null=True)
    ny = models.FloatField("NY-New York", blank=True, null=True)
    oh = models.FloatField("OH-Ohio", blank=True, null=True)
    ok = models.FloatField("OK-Oklahoma", blank=True, null=True)
    or1 = models.FloatField("OR-Oregon", blank=True, null=True)
    pa = models.FloatField("PA-Pennsylvania", blank=True, null=True)
    ri = models.FloatField("RI-Rhode Island", blank=True, null=True)
    sc = models.FloatField("SC-South Carolina", blank=True, null=True)
    sd = models.FloatField("SD-South Dakota", blank=True, null=True)
    tn = models.FloatField("TN-Tennessee", blank=True, null=True)
    tx = models.FloatField("TX-Texas", blank=True, null=True)
    ut = models.FloatField("UT-Utah", blank=True, null=True)
    va = models.FloatField("VA-Virginia", blank=True, null=True)
    vt = models.FloatField("VT-Vermont", blank=True, null=True)
    wa = models.FloatField("WA-Washington", blank=True, null=True)
    wi = models.FloatField("WI-Wisconsin", blank=True, null=True)
    wv = models.FloatField("WV-West Virginia", blank=True, null=True)
    wy = models.FloatField("WY-Wyoming", blank=True, null=True)
    ab = models.FloatField("AB-Alberta", blank=True, null=True)
    bc = models.FloatField("BC-British Columbia", blank=True, null=True)
    mb = models.FloatField("MB-Manitoba", blank=True, null=True)
    mx = models.FloatField("MX-Mexico", blank=True, null=True)
    nb = models.FloatField("NB-New Brunswick", blank=True, null=True)
    nl = models.FloatField("NL-Newfound/Labra", blank=True, null=True)
    ns = models.FloatField("NS-Nova Scotia", blank=True, null=True)
    nt = models.FloatField("NT-NW Territory", blank=True, null=True)
    on1 = models.FloatField("ON-Ontario", blank=True, null=True)
    pe = models.FloatField("PE-Prince ED. ISL", blank=True, null=True)
    qc = models.FloatField("QC- Quebec", blank=True, null=True)
    sk = models.FloatField("SK-Saskatchewan", blank=True, null=True)
    yt = models.FloatField("YT-Yukon", blank=True, null=True)
    total = models.FloatField("Total")
    idcustomer = models.ForeignKey(Customers, models.DO_NOTHING, db_column="idcustomer")
    history = HistoricalRecords()

    class Meta:
        managed = False
        db_table = 'millages'


class Recive(models.Model):
    idrecive = models.BigAutoField(primary_key=True)
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='idcustomer')
    year = models.CharField("Year", max_length=4)
    date = models.DateField("Date")
    zip = models.CharField("Zip Code", max_length=5, blank=True, null=True, default='')
    state = models.CharField("State", max_length=45)
    gallons = models.FloatField("Gallons", blank=True, null=True)
    miles = models.FloatField("Miles", blank=True, null=True)
    quarter = models.CharField("Quarter", max_length=4)
    idunit = models.CharField("Unit", max_length=45, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        managed = False
        db_table = 'recive'


class Drivers(models.Model):
    iddriver = models.BigAutoField(primary_key=True)
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='idcustomer')
    nombre = models.CharField('Full Name', max_length=150, blank=False, null=False)
    phone = models.CharField('Phone', max_length=45, blank=False, null=False)
    ssn = models.CharField('SSN', max_length=45, blank=False, null=False)
    cdl = models.CharField('CDL', max_length=45, blank=False, null=False)
    cdl_state = models.CharField('State CDL', max_length=45, blank=False, null=False)
    date_of_birth = models.DateField('Date of Birth', blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    medical_card_expiration_date = models.DateField('Medical Card Expiration', blank=True, null=True)
    preemp = models.BooleanField('Pre-Employment', default=False, blank=True, null=True)
    random_test = models.BooleanField('Random Test', default=False, help_text=True, null=True, blank=True)
    username_clearinghouse = models.CharField('User Clearinghouse', null=True, blank=True, max_length=45)
    password_clearinghouse = models.CharField('Password Clearinghouse', null=True, blank=True, max_length=45)
    queries = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=45, blank=False, null=False, default='Active')
    history = HistoricalRecords()

    class Meta:
        db_table = 'drivers'


def exams_directory(instance, filename):
    return 'customers/{0}/drivers/{1}/{2}/{3}'.format(instance.iddriver.idcustomer_id, instance.iddriver_id, 'exams', filename)

class Exams(models.Model):
    idexam = models.BigAutoField(primary_key=True)
    iddriver = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='iddriver')
    type = models.CharField('Type', max_length=45)
    dateexam = models.DateField('Exam Date')
    dateresult = models.DateField('Result Date', default='0001-01-01')
    result = models.CharField('Result', max_length=45)
    lote_number = models.CharField('Lote Number', max_length=45, default='', null=True, blank=True)
    lote_expiration = models.DateField('Lote Expiration', null=True, blank=True, default='0001-01-01')
    filename = models.CharField(max_length=200, null=True, blank=True)
    path = models.FileField(upload_to=exams_directory, validators=[FileExtensionValidator(['pdf'])], blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'exams'


class Notes(models.Model):
    idnote = models.BigAutoField(primary_key=True)
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='idcustomer')
    fullname = models.CharField(max_length=200)
    created_at = models.DateField('Date', auto_now=True)
    date_expiry = models.DateField(null=True, blank=True)
    note = models.TextField('Note', blank=False, null=False)
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column='iduser')
    highlight = models.BooleanField("Highlight", default=False)
    pin_up = models.BooleanField("Pin Up", default=False)
    status = models.CharField(max_length=15, default='Active', null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'notes'


class Payable(models.Model):
    idpayable = models.BigAutoField(primary_key=True)
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING, db_column='idcustomer')
    idinvoice = models.PositiveIntegerField()
    datetrans = models.DateField()
    nobill = models.CharField(max_length=45)
    cost = models.FloatField()
    typepaycost = models.CharField(max_length=45)
    amount = models.FloatField()
    typepayamount = models.CharField(max_length=45)
    iduser = models.PositiveIntegerField()
    typetrans = models.CharField(max_length=45)
    history = HistoricalRecords()

    class Meta:
        managed = False
        db_table = 'payable'


class Random(models.Model):
    idrandom = models.BigAutoField(primary_key=True)
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    quarter = models.IntegerField(default=0)
    type = models.CharField(max_length=45)
    iddriver = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='iddriver')
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'random'


class RandomTest(models.Model):
    year = models.CharField(max_length=4)
    type = models.CharField(max_length=45)
    quarter = models.IntegerField()
    random_drivers = models.IntegerField()
    idcustomer = models.ForeignKey('Customers', models.DO_NOTHING)
    iddriver = models.ForeignKey('Drivers', models.DO_NOTHING, blank=True, null=True)
    history = HistoricalRecords()


class Cards(models.Model):
    idcard = models.BigAutoField(primary_key=True)
    idcustomer = models.PositiveIntegerField()
    type = models.CharField(max_length=45, blank=True, null=True)
    _cardno_data = fields.EncryptedCharField(max_length=50, default="", null=True)
    cardno = fields.SearchField(hash_key="9ddiot5adt6tf7btt16xe", encrypted_field_name="_cardno_data")
    expdate = models.CharField(max_length=45)
    csc = models.CharField(max_length=45, blank=True, null=True)
    zipcode = models.CharField(max_length=45, blank=True, null=True, default=' ')
    status = models.CharField(max_length=45, default='Active')
    last_used = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'cards'

    def __str__(self):
        return '{0} {1} {2}'.format(self.cardno, self.idcustomer, self.expdate)


class Task(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='user')
    assigned_to = models.ManyToManyField(User, related_name='assigned_to', blank=True)
    priority = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    archived = models.BooleanField(default=False)
    archived_by = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True, related_name='archived_by')
    archived_at = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey(Projects, models.DO_NOTHING, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()


def customer_directory(instance, filename):
    return 'customers/{0}/{1}/{2}'.format(instance.customer.idcustomer, instance.folder, filename)


class Customer_Files(models.Model):
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    filename = models.CharField(max_length=200, null=True, blank=True)
    folder = models.CharField(max_length=45)
    path = models.FileField(upload_to=customer_directory, validators=[FileExtensionValidator(['pdf', 'docx', 'xlsx'])])
    uploading_date: datetime = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, related_name='uploaded_by_id')
    erased_by = models.ForeignKey(User, models.DO_NOTHING, related_name='erased_by_id', null=True, blank=True)
    erased = models.BooleanField(default=False)
    erased_file_date = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()


class News(models.Model):
    subject = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    src = models.FileField(upload_to='News', null=True, blank=True)
    public = models.BooleanField()
    show_to_groups = models.ManyToManyField(Group, blank=True)
    repeat = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_repeat = models.DateTimeField(null=True, blank=True)
    repeat_since = models.DateTimeField(auto_now=True)
    repeat_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()


class Email_Log(models.Model):
    subject = models.CharField(max_length=45)
    sent = models.BooleanField(default=False)
    sending_date = models.DateTimeField()
    email = models.CharField(max_length=255)
    invoice = models.ForeignKey(Invoices, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    history = HistoricalRecords()


class Florida_Tag(models.Model):
    classification_gvw = models.CharField(max_length=25)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()


class Fl_Tag_Price_Month(models.Model):
    month = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    florida_tag = models.ForeignKey(Florida_Tag, on_delete=models.DO_NOTHING)
    is_deleted = models.BooleanField(default=False)
    history = HistoricalRecords()