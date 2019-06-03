# global-site packages
from datetime import datetime

# django&restframework packges
from django.db import models
from django.contrib.auth.models import AbstractUser

# third-party packges

# my-own packages
# from resources.models import Resource

# Create your models here.

class UserProfile(AbstractUser):
    """
    普通用户（注册用户表）
    用户注册时必填字段为email&username&phone&password
    """
    #username/password/email字段继承自基类
    userID = models.AutoField(primary_key=True,verbose_name='用户ID')
    name = models.CharField(max_length=30,verbose_name='用户名')
    phone = models.CharField(unique=True,max_length=11,default='',verbose_name='电话')
    isExpert = models.BooleanField(default=False,verbose_name='是否专家')
    email = models.EmailField(unique=True,verbose_name='邮箱')
    user_add_time = models.DateTimeField(default=datetime.now,verbose_name='添加时间')

    class Meta:
        verbose_name = '普通用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class ExpertProfile(models.Model):
    """
    科技专家（专家信息表）
    """
    user = models.OneToOneField(UserProfile,primary_key=True,on_delete=models.CASCADE,to_field='userID',related_name='expert',verbose_name='专家ID')
    introduction = models.TextField(blank=True,null=True,verbose_name='自我介绍')
    constitution = models.CharField(max_length=255,blank=True,null=True,verbose_name='所在机构')
    realName = models.CharField(max_length=255,verbose_name='真实姓名')
    expert_add_time = models.DateTimeField(default=datetime.now,verbose_name='添加时间')
    #所在领域field
    #field = models.ForeignKey()

    class Meta:
        verbose_name = '科技专家'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.realName

# class Favorite(models.Model):
#     """
#     用户收藏的科技资源(用户收藏表)
#     """
#     userID = models.ForeignKey(UserProfile,to_field='userID',on_delete=models.CASCADE)
#     resourceID = models.ForeignKey(Resource,on_delete=models.CASCADE)
#     add_time = models.DateTimeField(default=datetime.now)
#
#     class Meta:
#         verbose_name = '用户收藏'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return str(self.userID)+'Favor'+str(self.resourceID)


class Follow(models.Model):
    """
    用户之间的关注关系(用户关注表)
    """
    userID = models.ForeignKey(UserProfile,related_name='follow',on_delete=models.CASCADE,verbose_name='关注者')
    followID = models.ForeignKey(ExpertProfile,default='',to_field='user',related_name='followed',on_delete=models.CASCADE,verbose_name='被关注者')
    add_time = models.DateTimeField(default=datetime.now,verbose_name = '添加时间')

    class Meta:
        verbose_name = '用户关注'
        verbose_name_plural = verbose_name
        unique_together = ('userID','followID')

    def __str__(self):
        return str(self.userID)+'Follow'+str(self.followID)

class Message(models.Model):
    """
    站内信(站内信息表)
    """
    messageID = models.AutoField(primary_key=True,verbose_name='消息ID')
    senderID = models.ForeignKey(UserProfile,related_name='sendmsg',on_delete=models.CASCADE,verbose_name='发送者ID')
    receiverID = models.ForeignKey(UserProfile,related_name='receivemsg',on_delete=models.CASCADE,verbose_name='接受者ID')
    content = models.TextField(verbose_name='内容')
    add_time = models.DateTimeField(default=datetime.now,verbose_name='发送时间')

    class Meta:
        verbose_name = '站内信'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.messageID

class ExpertCheckForm(models.Model):
    formID = models.AutoField(primary_key=True,verbose_name='专家认证申请表单编号')
    userID = models.ForeignKey(UserProfile,to_field='userID',on_delete=models.CASCADE,verbose_name='用户ID')
    isPass = models.BooleanField(default=False,verbose_name='是否通过')
    isCheck = models.BooleanField(default=False,verbose_name='是否被审核过')
    reason = models.TextField(verbose_name='管理员意见')
    adminID = models.IntegerField(null=True,verbose_name='管理员ID')
    introduction = models.TextField(verbose_name='个人简介')
    constitution = models.CharField(max_length=255,verbose_name='所在机构')
    realName = models.CharField(max_length=255,verbose_name='真实姓名')
    add_time = models.DateTimeField(default=datetime.now,verbose_name='申请时间')

    class Meta:
        verbose_name = '专家认证申请表单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.formID


# class Admin(AbstractUser):
#     """
#     系统管理员(管理员信息表)
#     """
#     #password/email字段继承自基类
#     adminID = models.IntegerField(primary_key=True,verbose_name='管理员ID')
#     phone = models.CharField(null=True,blank=True,max_length=11,verbose_name='电话')
#     add_time = models.DateTimeField(default=datetime.now,verbose_name='添加时间')
#     class Meta:
#         verbose_name = '管理员'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.adminID


class Fields(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='领域编号')
    field = models.CharField(max_length=100, unique=True, verbose_name='领域名称')
    fieldID = models.CharField(max_length=100, verbose_name='领域编号')
    type = models.CharField(max_length=20, verbose_name='资源类型')

    class Meta:
        verbose_name = '领域名称表单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.fieldID


class Tags(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="用户领域ID")
    userID = models.ForeignKey(UserProfile, to_field='userID', on_delete=models.CASCADE, verbose_name='用户ID')
    fieldID = models.ForeignKey(Fields, to_field='id', on_delete=models.CASCADE, verbose_name='用户领域')

    class Meta:
        verbose_name = '用户领域表单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.tagID


#class UserField(models.Model):
#    field = models.ForeignKey(Fields, on_delete=models.CASCADE, verbose_name='领域名称')
#    userID = models.ForeignKey(Tags , primary_key=True, on_delete=models.CASCADE, verbose_name='用户ID')
#
#    class Meta:
#        verbose_name = '用户领域表单'
#        verbose_name_plural = verbose_name
