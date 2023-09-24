import random


def getWaitingRoomUserDetail(userDetail):
    username = userDetail["username"]
    openId = userDetail["openId"]

    return {
        "username": username,
        "openId": openId,
        "status": False,
    }


# 查看游戏状态
def checkGameStatus(room_detail):
    firstUser = room_detail["firstUser"]
    secondUser = room_detail["secondUser"]

    if not firstUser["gameIsOver"]: return room_detail
    if not secondUser["gameIsOver"]: return room_detail

    # 如果用户的gameIsOver都为True，说明游戏已经结束
    room_detail["gameStatus"] = "done"

    # 判断用户的步数，判断谁胜利
    firstStep = int(firstUser["step"])
    secondStep = int(secondUser["step"])
    if firstStep > secondStep:
        room_detail["winner"] = secondUser['openId']
    elif firstStep < secondStep:
        room_detail["winner"] = firstUser['openId']

    return room_detail


def getSecretNumbers(number):
    secretList = []
    while len(secretList) < number:
        secretNum = random.randint(0, 9)
        if secretNum not in secretList:
            secretList.append(secretNum)
    return secretList
