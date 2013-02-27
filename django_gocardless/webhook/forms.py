from django import forms

from .models import GoCardlessWebhook


class GoCardlessWebhookForm(forms.ModelForm):

    class Meta:
        model = GoCardlessWebhook
