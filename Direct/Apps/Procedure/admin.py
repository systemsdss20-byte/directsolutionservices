from django.contrib.auth.admin import UserAdmin, GroupAdmin
from simple_history.admin import SimpleHistoryAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Services, User, Group, Invoice_paid, Cards
from django.contrib import admin


# Register your models here.
from ..Attendanceapp.models import Attendance


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'last_login', 'is_active', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('fullname', 'first_name', 'last_name', 'email', 'avatar')}),
        (('Permissions'), {'fields': ('change_password', 'is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'change_password', 'password1', 'password2')}
         ),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_active=True)


class CustomGroupAdmin(GroupAdmin):
    filter_horizontal = ('permissions', 'service')

class ServicesAdmin(admin.ModelAdmin):
    list_display = ('idservice', 'description', 'rate', 'cost')
    search_fields = ['idservice', 'description']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_active=True)

#admin.site.register(States)
admin.site.register(Services, ServicesAdmin)
# admin.site.register(Cards)
#admin.site.register(Attendance)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group,CustomGroupAdmin)
# admin.site.register(Invoice_paid, SimpleHistoryAdmin)
admin.site.register(Attendance)
#admin.site.register(Customers, SimpleHistoryAdmin)
#admin.site.register(Units, SimpleHistoryAdmin)