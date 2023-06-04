from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserForm, UpdateUserForm, UpdateUserCountForm
from .models import User
from utils import restful
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.core.cache import cache

appid = "wx9e48b38eda513483"
secret = "7c01f44918662846de2e11217cadbc91"


def get_user_info_by_openId(access_token, openid):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN'.format(access_token,
                                                                                                      openid)
    res = requests.get(url)
    user_info = res.json()
    return user_info


# 获取微信用户openid
def get_wx_openid(js_code):
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': appid,
        'secret': secret,
        'js_code': js_code,
        'grant_type': 'authorization_code'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


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


def _get_user_info_by_wx_url(openid):
    # 从缓存中获取 access_token
    access_token = cache.get('access_token')
    if not access_token:
        # 如果缓存中不存在 access_token，从微信 API 中获取
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(
            appid, secret)
        res = requests.get(url)
        access_token = res.json()['access_token']

        # 将 access_token 缓存
        cache.set('access_token', access_token, 7200)

    # 从微信 API 中获取用户信息
    user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN'.format(
        access_token, openid)
    print("user_info_url", user_info_url)
    res = requests.get(user_info_url)
    user_info = res.json()

    return user_info


@csrf_exempt
def get_user_info(request):
    data = json.loads(request.body)
    code = data.get('code')

    # 根据wx.login获取的临时code，获取openid
    wx_response = get_wx_openid(code)
    openid = wx_response.get("openid")
    print("openid", openid)

    # 根据返回的openid，获取用户信息（接口暂时不可用，不知道为什么用不了）
    # user_info = _get_user_info_by_wx_url(openid)

    # 如果openid不为空，则执行
    user_info = User.objects.filter(openId=openid).values().first() if openid else None
    if not user_info:
        user_info = {"username": "微信用户", "openid": openid}

    return restful.result(data=user_info)


# 获取用户信息
@csrf_exempt
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
            user.save()
            return restful.result(message="用户积分修改成功")
        else:
            return restful.params_error(message="用户不存在")
    else:
        message = "数据传参有误"
        response_data = {'errors': form.errors}
        return restful.params_error(message=message, data=response_data)
