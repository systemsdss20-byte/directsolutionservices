from .models import Commission_Percent
from django import forms


class Commission_PercentForm(forms.ModelForm):
    class Meta:
        model = Commission_Percent
        fields = '__all__'