from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .forms import UserForm, UpdateUserForm, UpdateUserCountForm
from .models import User, UserPkHistory
from utils import restful, waitRoom
from django.db.models import Q, Count
from django.db import models
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json
from django.core.cache import cache
import time

import redis
import random

r = redis.Redis(host="127.0.0.1", port=6379)

appid = "wxe16b90637ea98dcb"
secret = "ef084f49d04e38dbec0630c62eaf68c9"


# 获取随机id
def getId():
    roomId = str(random.random())
    roomId = roomId.split(".")[1]
    return roomId


def get_user_info_by_openId(access_token, openid):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={0}&openid={1}&lang=zh_CN'.format(access_token,
                                                                                                      openid)
    res = requests.get(url)
    user_info = res.json()
    return user_info


# 获取微信用户openid
def get_wx_openid(js_code, type="passwordDetective"):
    # 根据传入的type，判断是哪个小程序
    if type == "guessFourNumber":
        appid = "wx9e48b38eda513483"
        secret = "7c01f44918662846de2e11217cadbc91"
    else:
        appid = "wxe16b90637ea98dcb"
        secret = "ef084f49d04e38dbec0630c62eaf68c9"

    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': appid,
        'secret': secret,
        'js_code': js_code,
        'grant_type': 'authorization_code'
    }
    print(params)
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
@require_http_methods(["POST"])
def get_user_info(request):
    code = request.POST.get('code')
    openid = request.POST.get('openid')
    type = request.POST.get("type")

    if not type:
        type = "passwordDetective"

    if not openid:
        # 根据wx.login获取的临时code，获取openid
        wx_response = get_wx_openid(code, type)
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
@require_http_methods(["POST"])
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
@require_http_methods(["POST"])
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
@require_http_methods(["POST"])
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

        # 给UserCount进行判断
        if UserCount is None:
            UserCount = 0
        elif isinstance(UserCount, str):
            try:
                UserCount = int(UserCount)
            except ValueError:
                UserCount = 0

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
@require_http_methods(["POST"])
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


@csrf_exempt
@require_http_methods(["POST"])
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
@require_http_methods(["POST"])
def getRoomDetail(request):
    roomId = request.POST.get("roomId")
    if (roomId.find("room_id") == -1): roomId = "room_id_" + roomId

    room_id = roomId
    room_detail = r.get(room_id)
    if not room_detail:
        return restful.params_error(message="房间号有误！")

    room_detail = eval(room_detail)
    return restful.result(data=room_detail)


@csrf_exempt
@require_http_methods(["POST"])
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
@require_http_methods(["POST"])
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


@csrf_exempt
@require_http_methods(["POST"])
def get_rank(request):
    open_id = request.POST.get("open_id")

    user_count = User.objects.filter(openId=open_id).values_list('UserCount', flat=True).first()
    print(user_count)

    count = None
    if user_count is not None:
        # 获取大于 user_count 的数据条数
        count = User.objects.filter(Q(UserCount__gt=user_count) | Q(UserCount=None)).count()
        print(f"大于 {user_count} 的数据条数为：{count}")
    else:
        print("没有找到指定 open_id 的数据")

    count = count + 1 if count else None
    rank_detail = {'rank': count}
    return restful.result(message="获取数据成功", data=rank_detail)


@csrf_exempt
@require_http_methods(["POST"])
def get_top20_rank(request):
    top20_rank = User.objects.order_by('-UserCount')[:20]
    data = []

    for user_data in top20_rank.values():
        obj = {
            "nickname": user_data['nickname'],
            "UserCount": user_data['UserCount'],
            "cityValue": user_data['cityValue'],
        }
        data.append(obj)

    return restful.result(message="获取数据成功", data=data)


@csrf_exempt
@require_http_methods(["POST"])
def getWaitingRoom(request):
    username = request.POST.get("username")
    openId = request.POST.get("openId")
    waitingRoomId = request.POST.get("waitingRoomId")

    # 用户信息为必传
    if not username: return restful.params_error(message="请传入用户名")
    if not openId: return restful.params_error(message="请传入openID")

    # 如果有房间ID，则查询房间ID
    if waitingRoomId:
        waitingRoomDetail = r.get(waitingRoomId)
        if not waitingRoomDetail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

        waitingRoomDetail = eval(waitingRoomDetail)
        firstUser = waitingRoomDetail["firstUser"]
        secondUser = waitingRoomDetail["secondUser"]

        # 如果房间人数已满，则直接返回
        if firstUser["username"] and secondUser["username"]: return restful.params_error(message="房间已满，请重新创建")

        # 如果用户已经在房间内，则直接返回
        if firstUser["openId"] == openId or secondUser["openId"] == openId:
            return restful.params_error(message="您已经在房间内")

        # 如果firstUser为空，则赋值firstUser，否则赋值secondUser
        userDetail = {"username": username, "openId": openId}
        if not firstUser["username"]:
            waitingRoomDetail["firstUser"] = waitRoom.getWaitingRoomUserDetail(userDetail)
        else:
            waitingRoomDetail["secondUser"] = waitRoom.getWaitingRoomUserDetail(userDetail)

        # 如果没有房主，则当前用户为房主
        if not waitingRoomDetail["roomLeader"]: waitingRoomDetail["roomLeader"] = openId

        r.set(waitingRoomId, str(waitingRoomDetail), ex=604800)
        return restful.result(data=waitingRoomDetail)

    # 如果没有传入roomId，则直接创建一个房间，并返回
    if not waitingRoomId:
        waitingRoomId = "waitingRoom_id_" + getId()
        firstUser = waitRoom.getWaitingRoomUserDetail({"username": username, "openId": openId})
        secondUser = waitRoom.getWaitingRoomUserDetail({"username": "", "openId": ""})

        return_data = {
            "waitingRoomId": waitingRoomId,
            "roomLeader": openId,  # 房主
            "gameBeginStatus": False,  # 游戏开始状态，默认为False
            "firstUser": firstUser,
            "secondUser": secondUser,
        }

        r.set(waitingRoomId, str(return_data), ex=604800)
        return restful.result(data=return_data)


@csrf_exempt
@require_http_methods(["POST"])
def quitWaitingRoom(request):
    openId = request.POST.get("openId")
    waitingRoomId = request.POST.get("waitingRoomId")

    # 用户信息为必传
    if not waitingRoomId: return restful.params_error(message="房间ID为必传")
    if not openId: return restful.params_error(message="请传入openID")

    waitingRoomDetail = r.get(waitingRoomId)
    if not waitingRoomDetail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

    # 获取用户详情
    waitingRoomDetail = eval(waitingRoomDetail)
    firstUser = waitingRoomDetail["firstUser"]
    secondUser = waitingRoomDetail["secondUser"]
    roomLeader = waitingRoomDetail["roomLeader"]

    # 如果用户退出房间，则删除对应的用户信息
    if firstUser["openId"] == openId:
        waitingRoomDetail["firstUser"] = waitRoom.getWaitingRoomUserDetail({"username": "", "openId": ""})
    elif secondUser["openId"] == openId:
        waitingRoomDetail["secondUser"] = waitRoom.getWaitingRoomUserDetail({"username": "", "openId": ""})

    # 如果退出房间的为房主，则将另一个人归类为房主
    if roomLeader == openId:
        if firstUser["openId"]:
            waitingRoomDetail["roomLeader"] = firstUser["openId"]
        elif secondUser["openId"]:
            waitingRoomDetail["roomLeader"] = secondUser["openId"]
        else:
            waitingRoomDetail["roomLeader"] = ""

    # 保存到redis，并返回数据
    r.set(waitingRoomId, str(waitingRoomDetail), ex=604800)
    return restful.result(data=waitingRoomDetail)


@csrf_exempt
@require_http_methods(["POST"])
def checkWaitingRoom(request):
    waitingRoomId = request.POST.get("waitingRoomId")

    # 用户信息为必传
    if not waitingRoomId: return restful.params_error(message="房间ID为必传")

    waitingRoomDetail = r.get(waitingRoomId)
    if not waitingRoomDetail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

    # 获取用户详情
    waitingRoomDetail = eval(waitingRoomDetail)
    return restful.result(data=waitingRoomDetail)


# 更新waitingRoom用户状态
@csrf_exempt
@require_http_methods(["POST"])
def updateWaitingRoom(request):
    waitingRoomId = request.POST.get("waitingRoomId")
    username = request.POST.get("username")
    openId = request.POST.get("openId")
    status = request.POST.get("status")

    # 用户信息为必传
    if not waitingRoomId: return restful.params_error(message="房间ID为必传")
    if not username: return restful.params_error(message="username为必传")
    if not openId: return restful.params_error(message="openId为必传")
    if not status: return restful.params_error(message="status为必传")

    waitingRoomDetail = r.get(waitingRoomId)
    if not waitingRoomDetail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

    # 获取用户详情
    waitingRoomDetail = eval(waitingRoomDetail)
    firstUser = waitingRoomDetail["firstUser"]
    secondUser = waitingRoomDetail["secondUser"]

    if firstUser["openId"] == openId and status: firstUser["status"] = True
    if secondUser["openId"] == openId and status: secondUser["status"] = True

    r.set(waitingRoomId, str(waitingRoomDetail), ex=604800)
    return restful.result(data=waitingRoomDetail)


# 根据waitingRoom的ID获取比赛详情
@csrf_exempt
@require_http_methods(["POST"])
def getPkRoomFromWaitingRoom(request):
    waitingRoomId = request.POST.get("waitingRoomId")
    username = request.POST.get("username")
    openId = request.POST.get("openId")

    # 用户信息为必传
    if not waitingRoomId: return restful.params_error(message="房间ID为必传")
    if not username: return restful.params_error(message="username为必传")
    if not openId: return restful.params_error(message="openId为必传")

    # 将对应的ID转换成waitingBeginRoomID，并尝试从redis获取数据
    waitingBeginRoomId = waitingRoomId.replace("waitingRoom_id_", "waitingBeginRoom_id_")
    waitingBeginRoomDetail = r.get(waitingBeginRoomId)

    # ** 如果查询到房间对战详情，则直接返回
    if waitingBeginRoomDetail:  return restful.result(data=eval(waitingBeginRoomDetail))

    # ** 如果查询不到房间，则开始创建房间详情
    waitingRoomDetail = r.get(waitingRoomId)
    if not waitingRoomDetail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

    # 检查用户数据是否可用
    if True:
        # 获取用户详情
        waitingRoomDetail = eval(waitingRoomDetail)
        firstUser = waitingRoomDetail["firstUser"]
        secondUser = waitingRoomDetail["secondUser"]

        # 如果用户信息为空，说明房间人数不满
        if not firstUser["username"]: return restful.params_error(message="请等待用户进入房间")
        if not secondUser["username"]: return restful.params_error(message="请等待用户进入房间")

        # 如果用户还没准备，直接返回
        if not firstUser["status"]: return restful.params_error(message="用户尚未准备")
        if not secondUser["status"]: return restful.params_error(message="用户尚未准备")

    room_detail = {}  # 返回数据

    # 丰富返回信息
    room_detail["beginTime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    room_detail["roomId"] = "room_id_" + getId()
    room_detail["secretNumbers"] = waitRoom.getSecretNumbers(4)

    # firstUser用户信息
    firstUserDetail = {}
    firstUserDetail["username"] = firstUser["username"]
    firstUserDetail["openId"] = firstUser["openId"]
    firstUserDetail["useTime"] = ""
    firstUserDetail["step"] = 0
    firstUserDetail["gameStatus"] = False
    firstUserDetail["gameIsOver"] = False
    room_detail["firstUser"] = firstUserDetail

    # secondUser用户信息
    secondUserDetail = {}
    secondUserDetail["username"] = secondUser["username"]
    secondUserDetail["openId"] = secondUser["openId"]
    secondUserDetail["useTime"] = ""
    secondUserDetail["step"] = 0
    secondUserDetail["gameStatus"] = False
    secondUserDetail["gameIsOver"] = False
    room_detail["secondUser"] = secondUserDetail

    room_detail["gameStatus"] = "loading"
    room_detail["winner"] = ""

    # 需要更新gameBeginStatus
    waitingRoomDetail['gameBeginStatus'] = True
    r.set(waitingRoomId, str(waitingRoomDetail), ex=604800)

    # 创建两个房间的PKroom内容，虽然都是一样的，但是需要两个
    r.set(waitingBeginRoomId, str(room_detail), ex=604800)
    r.set(room_detail["roomId"], str(room_detail), ex=604800)
    return restful.result(message="进入房间成功", data=room_detail)


# 更新PK房间用户详情
@csrf_exempt
@require_http_methods(["POST"])
def updatePkRoomDetail(request):
    roomId = request.POST.get("roomId")
    username = request.POST.get("username")
    openId = request.POST.get("openId")
    step = request.POST.get("step")
    useTime = request.POST.get("useTime")
    gameStatus = request.POST.get("gameStatus")
    gameIsOver = request.POST.get("gameIsOver")

    # 用户信息为必传
    if not roomId: return restful.params_error(message="roomId为必传")
    if not username: return restful.params_error(message="username为必传")
    if not openId: return restful.params_error(message="openId为必传")

    room_detail = r.get(roomId)
    if not room_detail: return restful.params_error(message="查找房间失败")  # 如果没有查询到房间号，则直接返回

    # 获取用户信息
    room_detail = eval(room_detail)
    firstUser = room_detail["firstUser"]
    secondUser = room_detail["secondUser"]

    # 如果传入的用户是firstUser
    if firstUser["openId"] == openId:
        if step: firstUser["step"] = step
        if useTime: firstUser["useTime"] = useTime
        if gameStatus: firstUser["gameStatus"] = gameStatus
        if gameIsOver: firstUser["gameIsOver"] = gameIsOver

    # 如果传入的用户为secondUser
    elif secondUser["openId"] == openId:
        if step: secondUser["step"] = step
        if useTime: secondUser["useTime"] = useTime
        if gameStatus: secondUser["gameStatus"] = gameStatus
        if gameIsOver: secondUser["gameIsOver"] = gameIsOver

    else:  # 否则查询用户失败
        return restful.params_error(message="查询用户失败")

    room_detail = waitRoom.checkGameStatus(room_detail)  # 查询游戏是否已经结束

    r.set(room_detail["roomId"], str(room_detail), ex=604800)
    return restful.result(message="更新数据成功", data=room_detail)
