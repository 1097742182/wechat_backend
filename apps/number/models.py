from django.db import models


class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    openId = models.CharField(max_length=200, unique=True)
    nickname = models.CharField(max_length=200)
    # avatarUrl = models.ImageField(upload_to='images/')
    avatarUrl = models.CharField(max_length=200, default="")
    UserCount = models.CharField(max_length=200, default="")  # 用户分数
    LevelStep = models.CharField(max_length=200, default="")  # 用户关卡
    cityValue = models.CharField(max_length=200, default="")  # 用户关卡
    genderValue = models.CharField(max_length=200, default="")  # 用户关卡

    def __str__(self):
        return self.username
