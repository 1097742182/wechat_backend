from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required')
        return username

    def clean_openId(self):
        openId = self.cleaned_data.get('openId')
        if not openId:
            raise forms.ValidationError('OpenID is required')
        return openId


# forms.py
class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=200, error_messages={"max_length": '字符段不符合要求！'})
    openId = forms.CharField(max_length=200, error_messages={"max_length": '字符段不符合要求！'})

    class Meta:
        model = User
        exclude = ["username", "openId"]
