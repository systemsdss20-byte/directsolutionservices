from django import forms

from .models import Employee, Attendance


class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['names'].widget.attrs.update({'class': 'form-control'})
        self.fields['surnames'].widget.attrs.update({'class': 'form-control'})
        self.fields['timezone'].widget.attrs.update({'class': 'form-select form-select-sm'})

    class Meta:
        model = Employee
        fields = '__all__'


class AttendanceForm(forms.ModelForm):
    '''def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hours'].widget.attrs.update({'class': 'form-control'})
'''
    class Meta:
        model = Attendance
        # widgets = {
        #     'clock_in_at': forms.TimeInput(format='%H:%M:%S', attrs={'class': 'form-control form-control-sm', 'type': 'time'}),
        # }
        fields = '__all__'