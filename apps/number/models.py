from django.db import models
from django.utils import timezone


class User(models.Model):
    openId = models.CharField(max_length=200, unique=True)
    session_key = models.CharField(max_length=200, default="", null=True, blank=True)
    nickname = models.CharField(max_length=200, null=True, blank=True)
    # avatarUrl = models.ImageField(upload_to='images/')
    avatarUrl = models.CharField(max_length=200, default="", null=True, blank=True)
    UserCount = models.IntegerField(default=0, null=True, blank=True)  # 用户分数
    LevelStep = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    HardLevelStep = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    cityValue = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    genderValue = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    createTime = models.DateTimeField(default=timezone.now)
    objects = models.Manager()  # 的管理器

    def __str__(self):
        return self.nickname


class UserPkHistory(models.Model):
    openId = models.CharField(max_length=200, unique=True)
    UserGameDetail = models.CharField(max_length=200)
    PkHistoryList = models.TextField(blank=True, null=True)
    objects = models.Manager()  # 的管理器


class GameHistory(models.Model):
    id = models.AutoField(primary_key=True)
    beginTime = models.DateTimeField()
    roomId = models.IntegerField()

    firstUser = models.CharField(max_length=255)
    firstOpenId = models.CharField(max_length=255)
    firstUseTime = models.CharField(max_length=255)
    firstStep = models.SmallIntegerField()
    firstReady = models.BooleanField(default=False)
    firstGameStatus = models.BooleanField(default=False)

    secondUser = models.CharField(max_length=255)
    secondOpenId = models.CharField(max_length=255)
    secondUseTime = models.CharField(max_length=255)
    secondStep = models.SmallIntegerField()
    secondReady = models.BooleanField(default=False)
    secondGameStatus = models.BooleanField(default=False)

    gameStatus = models.CharField(max_length=20)

    class Meta:
        db_table = 'game_history'
