# global-site packages
from datetime import datetime

# django&restframework packges
from django.db import models

# third-party packges

# my-own packages
from users.models import UserProfile

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




#
# class Resource(models.Model):
#     """
#     科技资源(资源信息表)
#     """
#     RES_TYPE = (
#         (1,'论文'),
#         (2,'专利'),
#     )
#
#     resourceID = models.AutoField(primary_key=True,verbose_name='资源ID')
#     intro = models.TextField(default='',max_length=255,verbose_name='资源介绍')
#     type = models.IntegerField(choices=RES_TYPE,verbose_name='资源类别')
#     #资源评分是5分制
#     score = models.FloatField(default=0,verbose_name='资源评分')
#     date = models.DateTimeField(verbose_name='发表时间')
#     ownerID = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
#     #path是指？
#     path = models.CharField(max_length=255)
#     name = models.CharField(max_length=255,verbose_name='资源名称')
#     field = models.ForeignKey()
#
# class Paper(Resource):
#     """
#     论文(论文信息表)
#     """
#     paperID = models.ForeignKey(Resource,on_delete=models.CASCADE,to_field='resourceID')
#     doi = models.CharField()
#     #?
#     docType = models.IntegerField()
#     paperTitle = models.CharField()
#     originalTitle = models.CharField()
#     bookTitle = models.CharField()
#     year = models.IntegerField()
#     date = models.DateField()
#     pulisher = models.CharField()
#     journal = models.CharField()
#     conference = models.CharField()
#     volume = models.CharField()
#     issue = models.CharField()
#     firstPage = models.CharField()
#     lastPage = models.CharField()
#     refCount = models.IntegerField()
#     citCount = models.IntegerField()
#     createdDate = models.DateField()
#     resourceURL = models.CharField()
#
# class CitationContest(models.Model):
#     """
#     论文被引表
#     """
#     paperID = models.ForeignKey(Paper,primary_key=True,on_delete=models.CASCADE,to_field='paperID')
#     paperReferenceID = models.IntegerField
#     citationContext = models.TextField
#
# class paperReference(models.Model):
#     """
#     论文引用表
#     """
#     paperID =
#
#
# class Patent(Resource):
#     """
#     专利(专利信息表)
#     """
#     patentID = models.ForeignKey(Resource,on_delete=models.CASCADE,primary_key=True,to_field='resourceID')
#     primaryClass = models.CharField()
#     applicationNumber = models.IntegerField()
#     title = models.CharField()
#     countryProvince = models.CharField()
#     publicationDate = models.DateField()
#     authorizedAnnouncementDate = models.DateField()
#     otherClasses =
#     applicationAddress = models.CharField
#     currentRightHolder = models.CharField
#     assignee =
#     keyWords =
#     filingDate = models.DateField
#     publicationNumber = models.IntegerField
#     authorizedPublicNumber = models.IntegerField
#     applicant = models.CharField
#     inventors =
#     agent =
#     priority = models.CharField
#     currentState = models.BooleanField
#     summary = models.TextField
#
# class Comment(models.Model):
#     """
#     对资源的评论（资源评论表）
#     """
#     commentID = models.AutoField(primary_key=True)
#     content = models.TextField()
#     date = models.DateTimeField()
#     userID = models.ForeignKey(UserProfile,on_delete=models.CASCADE,to_field='userID')
#     score = models.FloatField
#     resourceID = models.ForeignKey(Resource,on_delete=models.CASCADE,to_field='resourceID')
#     priorComment = models.ForeignKey('self',null=True,blank=True,to_field='commentID',
#                                      related_name='reply',on_delete=models.CASCADE)
#
