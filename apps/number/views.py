from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserForm, UpdateUserForm, UpdateUserCountForm
from .models import User, UserPkHistory
from utils import restful
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.core.cache import cache
import time

import redis
import random

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
    code = request.POST.get('code')
    openid = request.POST.get('openid')

    if not openid:
        # 根据wx.login获取的临时code，获取openid
        wx_response = get_wx_openid(code)
        openid = wx_response.get("openid")

    print("openid", openid)

    # 根据返回的openid，获取用户信息（接口暂时不可用，不知道为什么用不了）
    # user_info = _get_user_info_by_wx_url(openid)

    # 如果openid不为空，则执行
    if openid:
        user_info = User.objects.filter(openId=openid).values().first()
        user_pk_history = UserPkHistory.objects.filter(openId=openid).values().first()

        if user_pk_history:
            user_info.update(user_pk_history)

    else:
        user_info = None

    # 如果没有找到user_info，则赋予默认值进行返回
    if not user_info:
        user_info = {"nickname": "", "openId": openid, "isNewData": True}

        # 如果没有找到user_info，但是有openid，说明是新用户，则保存数据到数据库中
        User.objects.create(openId=openid).save() if openid else None

    return restful.result(data=user_info)


# 添加数据
@csrf_exempt
def add_data(request):
    form = UserForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        # user.genderValue = "男女"
        user.save()
        response_data = {
            "openId": user.openId,
            'nickname': user.nickname,
            'avatarUrl': user.avatarUrl,
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
        openId = form.cleaned_data.get('openId')
        if openId:
            try:
                user = User.objects.get(openId=openId)
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
        nickname = form.cleaned_data.get('nickname')
        openId = form.cleaned_data.get('openId')
        UserCount = form.cleaned_data.get('UserCount')
        user = None
        if openId:
            user = User.objects.filter(openId=openId).first()
        elif nickname:
            user = User.objects.filter(nickname=nickname).first()

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


# 更新PK历史数据
@csrf_exempt
def update_user_pk_history(request):
    openId = request.POST.get('openId')
    UserGameDetail = request.POST.get('UserGameDetail')
    PkHistoryList = request.POST.get('PkHistoryList')

    if not openId:
        return restful.params_error(message='openid不可为空')

    user_pk_history = UserPkHistory.objects.filter(openId=openId).first()
    # 如果查询到用户，则开始修改数据
    if user_pk_history:
        if UserGameDetail:  # 如果有传入UserGameDetail
            user_pk_history.UserGameDetail = str(UserGameDetail)
        if PkHistoryList:  # 如果有传入PkHistoryList
            user_pk_history.PkHistoryList = str(PkHistoryList)

        user_pk_history.save()

    return restful.result(message="用户PK数据修改成功")


r = redis.Redis(host="127.0.0.1", port=6379)


@csrf_exempt
def createRoom(request):
    firstUser = request.POST.get("username")
    firstOpenId = request.POST.get("openId")

    if firstUser is None or firstOpenId is None:
        return restful.params_error(message="信息有误，请确认用户信息")

    roomId = str(random.random())
    roomId = roomId.split(".")[1]

    # 存放数据
    room_detail = {"firstUser": firstUser, "firstOpenId": firstOpenId}
    room_detail = str(room_detail)

    # 将数据存放到Redis中
    room_id = "room_id_" + roomId
    r.set(room_id, room_detail, ex=604800)

    return restful.result(message="创建房间成功", data={"roomId": roomId})


@csrf_exempt
def getRoomDetail(request):
    roomId = request.POST.get("roomId")
    room_id = "room_id_" + roomId
    room_detail = r.get(room_id)
    if not room_detail:
        return restful.params_error(message="房间号有误！")

    room_detail = eval(room_detail)
    return restful.result(data=room_detail)


@csrf_exempt
def searchRoom(request):
    roomId = request.POST.get("roomId")
    username = request.POST.get("username")
    openId = request.POST.get("openId")

    # 获取对应roomId的信息
    room_id = "room_id_" + roomId
    room_detail = r.get(room_id)
    if not room_detail:  # 如果没有找到房间号
        return restful.params_error(message="房间ID号不存在")

    # 判断是否已经有secondUser，如果有，则直接返回
    room_detail = eval(room_detail)
    if room_detail.get("secondUser"):
        return restful.params_error(message="房间对战已开始，请重新创建房间")

    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # 丰富返回信息
    room_detail["beginTime"] = t
    room_detail["roomId"] = roomId
    room_detail["secondUser"] = username
    room_detail["secondOpenId"] = openId
    room_detail["secondStep"] = 0
    room_detail["firstStep"] = 0
    room_detail["gameStatus"] = "loading"

    room_detail["firstReady"] = False
    room_detail["secondReady"] = False

    r.set(room_id, str(room_detail), ex=604800)
    return restful.result(message="进入房间成功", data=room_detail)


@csrf_exempt
def updateRoomDetail(request):
    openId = request.POST.get("openId")
    userStep = request.POST.get("userStep")
    userUseTime = request.POST.get("userUseTime")
    roomId = request.POST.get("roomId")

    # 获取对应roomId的信息
    room_id = "room_id_" + roomId
    room_detail = r.get(room_id)
    if not room_detail:
        return restful.params_error(message="")

    room_detail = eval(room_detail)
    firstOpenId = room_detail.get("firstOpenId")
    secondOpenId = room_detail.get("secondOpenId")

    # 判断是否为第一个openId
    if openId == firstOpenId:
        room_detail['firstStep'] = userStep
        room_detail['firstUseTime'] = userUseTime
    # 判断是否为第二个openId
    elif openId == secondOpenId:
        room_detail['secondStep'] = userStep
        room_detail['secondUseTime'] = userUseTime

    r.set(room_id, str(room_detail), ex=604800)
    return restful.result(message="更新数据成功", data=room_detail)


@csrf_exempt
def deleteAllRoomIds(request):
    # 找到所有包含 room_id_ 字段的键
    keys = r.keys('room_id_*')

    # 删除这些键
    for key in keys:
        r.delete(key)

    return restful.result(message="删除所有key成功")
