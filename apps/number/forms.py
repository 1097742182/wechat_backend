from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = []

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if not nickname:
            raise forms.ValidationError('nickname is required')
        return nickname

    def clean_openId(self):
        openId = self.cleaned_data.get('openId')
        if not openId:
            raise forms.ValidationError('OpenID is required')
        return openId

    def clean(self):
        nickname = self.cleaned_data.get('nickname')
        if not nickname :
            raise forms.ValidationError('nickname is required')
        return self.cleaned_data


# forms.py
class UpdateUserForm(forms.ModelForm):
    nickname = forms.CharField(max_length=200, error_messages={"max_length": '字符段不符合要求！'})
    openId = forms.CharField(max_length=200, error_messages={"max_length": '字符段不符合要求！'})

    class Meta:
        model = User
        exclude = ["nickname", "openId"]


class UpdateUserCountForm(forms.Form):
    nickname = forms.CharField(max_length=200, required=False, error_messages={"max_length": '字符段不符合要求！'})
    openId = forms.CharField(max_length=200, required=False, error_messages={"max_length": '字符段不符合要求！'})
    UserCount = forms.IntegerField()

    def clean_UserCount(self):
        count = self.cleaned_data['UserCount']
        if count <= 0:
            raise forms.ValidationError("UserCount 应该大于0")
        return count

    def clean(self):
        nickname = self.cleaned_data.get('nickname')
        openId = self.cleaned_data.get('openId')
        if not nickname and not openId:
            raise forms.ValidationError('请至少使用昵称或openId中的一个来注册。')
        return self.cleaned_data
