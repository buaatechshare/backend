# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin
from rest_framework import viewsets,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# third-party packges
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

# my-own packages
from .serializers import UserRegSerializer,MessageSerializer,FollowSerializer
from .models import UserProfile,Message,Follow

# Create your views here.

class UserViewSet(CreateModelMixin,
                  viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = UserProfile.objects.all()

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
                     #RetrieveModelMixin,
                     #ListModelMixin,
                     viewsets.GenericViewSet):
    """
    站内信
    """
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    #GET /messages/?senderID=xxx&receiverID=yyy/
    def get(self,request):
        senderID = request.query_params.get('senderID')
        receiverID = request.query_params.get('receiverID')
        queryset = Message.objects.filter(senderID=senderID,receiverID=receiverID)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class FollowViewSet(CreateModelMixin,
                    RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    用户关注
    """
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
