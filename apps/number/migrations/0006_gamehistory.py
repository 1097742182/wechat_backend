# Generated by Django 3.0.8 on 2023-09-01 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('number', '0005_userpkhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('beginTime', models.DateTimeField()),
                ('roomId', models.IntegerField()),
                ('firstUser', models.CharField(max_length=255)),
                ('firstOpenId', models.CharField(max_length=255)),
                ('firstUseTime', models.CharField(max_length=255)),
                ('firstStep', models.SmallIntegerField()),
                ('firstReady', models.BooleanField(default=False)),
                ('firstGameStatus', models.BooleanField(default=False)),
                ('secondUser', models.CharField(max_length=255)),
                ('secondOpenId', models.CharField(max_length=255)),
                ('secondUseTime', models.CharField(max_length=255)),
                ('secondStep', models.SmallIntegerField()),
                ('secondReady', models.BooleanField(default=False)),
                ('secondGameStatus', models.BooleanField(default=False)),
                ('gameStatus', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'game_history',
            },
        ),
    ]