"""Direct URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .Apps.Procedure import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.login_user, name='index'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('Procedure/', include('Direct.Apps.Procedure.urls'), name='Procedure'),
    path('Accounting/', include('Direct.Apps.Accounting.urls'), name='Accounting'),
    path('Attendance/', include('Direct.Apps.Attendanceapp.urls'), name='Attendanceapp'),
    path('AuditLogs/', include('Direct.Apps.AuditLogs.urls'), name='AuditLogs'),
    path('calendar/', include('Direct.Apps.Calendar.urls'), name='Calendar'),
    path('CallLists/', include('Direct.Apps.CallLists.urls'), name='CallLists'),
    path('Consortium/', include('Direct.Apps.Consortium.urls'), name='Consortium'),
    path('Fueltaxes/', include('Direct.Apps.FueltaxesApi.urls'), name='FueltaxesApi'),
    path('Reports/', include('Direct.Apps.Reports.urls'), name='Reports'),
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('site/favicon.ico')))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404='Direct.Apps.Procedure.views.handler404'