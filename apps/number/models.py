from django.db import models


class User(models.Model):
    openId = models.CharField(max_length=200, unique=True)
    session_key = models.CharField(max_length=200, default="", null=True, blank=True)
    nickname = models.CharField(max_length=200, null=True, blank=True)
    # avatarUrl = models.ImageField(upload_to='images/')
    avatarUrl = models.CharField(max_length=200, default="", null=True, blank=True)
    UserCount = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户分数
    LevelStep = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    cityValue = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡
    genderValue = models.CharField(max_length=200, default="", null=True, blank=True)  # 用户关卡

    def __str__(self):
        return self.nickname
