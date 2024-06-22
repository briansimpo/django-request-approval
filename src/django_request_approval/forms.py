

from django import forms
from .models import ApprovalStatus


class ApprovalForm(forms.Form):

    comment = forms.CharField(required=True, label="Comment")
    decision = forms.ChoiceField(choices=ApprovalStatus.choices, required=True, label="Decision")

    class Meta:
        fields = ["comment", "decision"]
   
