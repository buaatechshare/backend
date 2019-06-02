# global-site packages
from datetime import datetime

# django&restframework packges
from django.db import models

# third-party packges

# my-own packages
from users.models import UserProfile,ExpertProfile

# Create your models here.

class Comment(models.Model):
    """
    资源评论表
    """
    commentID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(UserProfile,to_field='userID',on_delete=models.CASCADE)
    resourceID = models.CharField(max_length=255)
    content = models.TextField()
    rate = models.IntegerField()
    add_time = models.DateTimeField(default=datetime.now,)

class Collection(models.Model):
    """
    用户收藏表
    """
    userID = models.ForeignKey(UserProfile,to_field='userID',on_delete=models.CASCADE)
    resourceID = models.CharField(max_length=255)
    add_time = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('userID','resourceID')

class PaperCheckForm(models.Model):
    userID = models.ForeignKey(ExpertProfile,to_field='user',on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    doi = models.CharField(max_length=255)
    abstract = models.TextField()
    file = models.FileField(upload_to='papers/',verbose_name='上传的论文')
    isCheck = models.BooleanField(default=False,verbose_name='是否被审核过')
    isPass = models.BooleanField(default=False,verbose_name='是否通过')
    add_time = models.DateTimeField(default=datetime.now)