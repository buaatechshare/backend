# Generated by Django 2.1.8 on 2019-06-03 07:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resourceID', models.CharField(max_length=255)),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('commentID', models.AutoField(primary_key=True, serialize=False)),
                ('resourceID', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('rate', models.IntegerField()),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='PaperCheckForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('doi', models.CharField(max_length=255)),
                ('abstract', models.TextField()),
                ('file', models.FileField(upload_to='papers/', verbose_name='上传的论文')),
                ('isCheck', models.BooleanField(default=False, verbose_name='是否被审核过')),
                ('isPass', models.BooleanField(default=False, verbose_name='是否通过')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
