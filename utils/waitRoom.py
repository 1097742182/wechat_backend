def getWaitingRoomUserDetail(userDetail):
    username = userDetail["username"]
    openId = userDetail["openId"]

    return {
        "username": username,
        "openId": openId,
        "status": False,
    }
