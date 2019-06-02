# global-site packages
from datetime import datetime


# django&restframework packges
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import logging
from django.core import serializers
# third-party packges
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

# my-own packages
from .serializers import UserRegSerializer,MessageGetSerializer,MessagePostSerializer,FollowGetSerializer,FollowPostSerializer,UserDetailSerializer,UserUpdateSerializer
from .serializers import ExpertApplySerializer
from .models import UserProfile,Message,Follow,ExpertCheckForm,ExpertProfile

# Create your views here.

#pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    max_page_size = 100


class UserViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    用户
    """
    #serializer_class = UserRegSerializer
    queryset = UserProfile.objects.all()

    #根据请求类型POST/GET/PUT(PATCH)，使用不同的serializer
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserDetailSerializer

    # #获取当前登录的用户，返回用户信息
    # def get_object(self):
    #     return self.request.user

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['userID'] = user.userID

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED,
                        headers=headers)


class MessageViewSet(CreateModelMixin,
                     ListModelMixin,
                     viewsets.GenericViewSet):
    """
    站内信
    """
    queryset = Message.objects.all()
    pagination_class = StandardResultsSetPagination

    #根据请求类型POST/GET/PUT(PATCH)，使用不同的serializer
    def get_serializer_class(self):
        if self.action == 'list':
            return MessageGetSerializer
        return MessagePostSerializer

    #GET /messages/?senderID=xxx&receiverID=yyy/
    def list(self, request, *args, **kwargs):
        senderID = request.query_params.get('senderID')
        receiverID = request.query_params.get('receiverID')
        if senderID and receiverID:
            queryset = Message.objects.filter(senderID=senderID,receiverID=receiverID)
        elif senderID:
            queryset = Message.objects.filter(senderID=senderID)
        elif receiverID:
            queryset = Message.objects.filter(receiverID=receiverID)
        else:
            queryset = []
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class FollowViewSet(CreateModelMixin,
                    RetrieveModelMixin,
                    DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    create:
        创建一条用户关注专家的记录
    read:
        根据userID列出他关注的所有专家
    delete:
        取关
    """
    queryset = Follow.objects.all()
    pagination_class = StandardResultsSetPagination

    #根据请求类型POST/GET/PUT(PATCH)，使用不同的serializer
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return FollowGetSerializer
        return FollowPostSerializer

    #GET /follow/{id}/
    def retrieve(self, request, *args, **kwargs):
        queryset = Follow.objects.filter(userID=kwargs['pk'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #DELETE /follow/{id}/?followID=xxx
    def destroy(self, request, *args, **kwargs):
        instance = Follow.objects.filter(userID=kwargs['pk'],followID=request.query_params.get('followID'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExpertCheckViewSet(CreateModelMixin,
                         ListModelMixin,
                         UpdateModelMixin,
                         RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    read:
        列出指定的表单
    list:
        列出所有未经审核的专家申请表单
    create:
        用户提交申请表单
    update:
        管理员审核表单
    patial_update:
        管理员审核表单
    """
    queryset = ExpertCheckForm.objects.all()
    pagination_class = StandardResultsSetPagination

    #根据请求类型POST/GET/PUT(PATCH)，使用不同的serializer
    def get_serializer_class(self):
        if self.action == 'create':
            return ExpertApplySerializer
        elif self.action == 'list' or self.action == 'update' or self.action == 'partial_update':
            return ExpertCheckSerializer
        return ExpertCheckSerializer

    #用户提交“专家申请审核表单”
    #POST /applications/
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    #管理员查看所有isCheck=False的表单
    #GET /applicaitons/
    def list(self, request, *args, **kwargs):
        queryset = ExpertCheckForm.objects.filter(isCheck=False)
        #queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #管理员根据userID获取表单(迷惑行为？？？
    #GET /applicaiton/{id}
    def retrieve(self, request, *args, **kwargs):
        queryset = ExpertCheckForm.objects.filter(userID=kwargs['pk'],isCheck=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #管理员审核（更新）表单
    #PUT/PATCH /applications/{formID}
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if serializer.validated_data.get('isPass'):
            user = serializer.validated_data.get('userID')
            introduction = serializer.validated_data.get('introduction')
            constitution = serializer.validated_data.get('constitution')
            realName = serializer.validated_data.get('realName')

            user = UserProfile.objects.get(userID=user.userID)
            user.isExpert=True
            user.save()

            expert = ExpertProfile(user=user,introduction=introduction,constitution=constitution,realName=realName)
            expert.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)



