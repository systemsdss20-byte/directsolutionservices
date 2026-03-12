import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler import util
from django_apscheduler.models import DjangoJobExecution
import atexit
from ..helpers.send_email import SendTemplateEmail
from ..Procedure.models import Customers
from ... import settings


# Create your views here.
def sendEmail_birthday():
    subject = list()
    recipients = list()
    context = list()
    today = datetime.date.today()
    template = 'Email/customer_birthday.html'
    try:
        customers = Customers.objects.filter(explic__month=today.month, explic__day=today.day, clientstatus="Active").values('email', 'owner')
        count = customers.count()
        if count != 0:
            for customer in customers:
                owner = "client"
                if customer["owner"]:
                    owner = customer["owner"]
                subject.append(f'Happy Birthday {owner}')
                context.append({'name': owner})
                recipients.append(customer["email"])
            SendTemplateEmail(
                template=template, subjects=subject, recipients=recipients, context=context,
                images=['dss.png', 'cake.png']).start()
            print("Email sent")
        print("Task Birthday executed")
    except Exception as e:
        print(f"Error CRON sending email {e}")


def start():
    try:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.add_job(
            sendEmail_birthday,
            trigger=CronTrigger(hour=7, minute=0),
            id="CustomerBirthday",
            max_instance=1,
            replace_existing=True,
            coalesce=True,
            misfire_grace_time=10,
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
    except Exception as e:
        print(e)
