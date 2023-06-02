from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserForm, UpdateUserForm
from utils import restful
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def get_data(request):
    data = [{
        "content": "test",
        "count": 10
    }]
    return restful.result(data=data)


def upload(request):
    if request.method == 'POST' and request.FILES['']:
        # myfile = request.FILES['file']
        # fs = FileSystemStorage()
        # uploaded_file_url = fs.url(filename)
        data = {'uploaded_file_url': 123}

        return restful.result(data=data)


# 添加数据
@csrf_exempt
def add_data(request):
    forms = UserForm(request.POST)
    if forms.is_valid():
        user = forms.save(commit=False)
        user.genderValue = "男女"
        user.save()
        response_data = {
            'status': 'success',
            'message': 'User updated successfully',
            'user': {
                'username': user.username,
                "openId": user.openId,
                'nickname': user.nickname,
                'avatarUrl': user.avatarUrl,
            }
        }
        return restful.result(data=response_data)

    else:
        message = "数据传参有误"
        response_data = {
            'errors': forms.errors,
        }
        return restful.params_error(message=message, data=response_data)


# 更新数据
@csrf_exempt
def update_data(request):
    forms = UpdateUserForm(request.POST)
    if forms.is_valid():
        username = forms.cleaned_data.get('username')
        openId = forms.cleaned_data.get('openId')
        nickname = forms.cleaned_data.get('nickname')
        print(username, openId, nickname)
        return restful.result()

    else:
        message = "数据传参有误"
        response_data = {
            'errors': forms.errors,
        }
        return restful.params_error(message=message, data=response_data)
