from django import forms

from ..Consortium.models import Comments


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment", "created_by", "detail_random_list"]

