from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserForm, UpdateUserForm, UpdateUserCountForm
from .models import User
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

# 获取用户信息
def get_user(request):
    username = request.POST.get('username', '')
    openId = request.POST.get('openId', '')
    if username:
        user = User.objects.filter(username=username).values().first()
    elif openId:
        user = User.objects.filter(openId=openId).values().first()
    else:
        return JsonResponse({'error': '参数错误'})
    if user:
        return JsonResponse(user, safe=False)
    return JsonResponse({'error': '未查询到用户'})


# 添加数据
@csrf_exempt
def add_data(request):
    form = UserForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        # user.genderValue = "男女"
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
            'errors': form.errors,
        }
        return restful.params_error(message=message, data=response_data)


# 更新数据
@csrf_exempt
def update_data(request):
    form = UpdateUserForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                user_fields = [f.name for f in User._meta.get_fields()]  # 获取User模型的所有字段
                for field in user_fields:
                    value = request.POST.get(field)
                    if value:
                        setattr(user, field, value)
                user.save()
                return restful.result(message="用户修改成功")

            except User.DoesNotExist:
                return restful.params_error(message="用户不存在")
        else:
            return restful.params_error(message="缺少必要的参数")
    else:
        message = "数据传参有误"
        response_data = {'errors': form.errors}
        return restful.params_error(message=message, data=response_data)


@csrf_exempt
def update_UserCount(request):
    form = UpdateUserCountForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        openId = form.cleaned_data.get('openId')
        UserCount = form.cleaned_data.get('UserCount')
        user = None
        if openId:
            user = User.objects.filter(openId=openId).first()
        elif username:
            user = User.objects.filter(username=username).first()

        # 处理找到的用户
        if user:
            user.UserCount = UserCount
            return restful.result(message="用户积分修改成功")
        else:
            return restful.params_error(message="用户不存在")
    else:
        message = "数据传参有误"
        response_data = {'errors': form.errors}
        return restful.params_error(message=message, data=response_data)
