# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework import viewsets,status
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse, HttpResponse

# third-party packges
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.views import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from elasticsearch import helpers
from resources.es_connect import es
# my-own packages
from .serializers import UserRegSerializer,MessageGetSerializer,MessagePostSerializer,FollowGetSerializer,FollowPostSerializer,UserDetailSerializer,UserUpdateSerializer
from .serializers import ExpertApplySerializer,ExpertCheckSerializer
from .serializers import FieldsSerializer,TagSerializer
from .models import Tags,UserProfile,Message,Follow,ExpertCheckForm,ExpertProfile, Fields
from backend.settings import EXPERT_OFFSET

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
    #PUT/PATCH /application/{formID}
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if serializer.validated_data.get('isPass'):
            expertID = serializer.validated_data.get('expertID')
            user = serializer.validated_data.get('userID')
            introduction = serializer.validated_data.get('introduction')
            constitution = serializer.validated_data.get('constitution')
            realName = serializer.validated_data.get('realName')

            user = UserProfile.objects.get(userID=user.userID)
            user.isExpert=True
            user.save()

            expertEntity = dict()
            if not expertID:
                expertID = int(user.userID)+EXPERT_OFFSET
                expertEntity["id"]=expertID
                expertEntity["name"]=realName
                expertEntity["normalized_name"]=realName
                expertEntity["pubs"]=[]
                expertEntity["n_pubs"]=0
                expertEntity["n_citation"]=0
            else:
                # update authors info in ES
                expertEntity=es.get(index="authors",id=expertID)["_source"]
            expert = ExpertProfile(expertID=str(expertID),user=user,introduction=introduction,constitution=constitution,realName=realName)
            expert.save()

            #向es.authors插入专家数据
            try:
                action = {
                    "_index": "authors",
                    "_type": "author",
                    "_id": expertID,
                    "_source": expertEntity
                }
                a = helpers.bulk(es, [action])
            except Exception:
                user.isExpert = False
                user.save()
                expert.delete()
                return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

def jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.

    Example:

    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }

    """
    return {
        'token': token,
        'userID': user.userID,
        'name': user.name,
        'isExpert': user.isExpert,
    }

class MyJSONWebTokenAPIView(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            #管理员登录
            if request.data['isAdmin']:
                if serializer.validated_data.get('user').isAdmin == False:
                    return Response(serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#返回用户名的模糊查询
#GET /receiver/{userName}/
def get_user_fuzzy_by_name(request, userName):
    fuzzy_name_set = UserProfile.objects.filter(name__icontains=userName)[:10]
    fuzzy_name = []
    for i in fuzzy_name_set:
        fuzzy_name.append((i.name,i.userID))
    name_dict = dict()
    name_dict['user'] = fuzzy_name
    return JsonResponse(name_dict, safe=False)




# 返回推荐专利


class FieldViewSet(CreateModelMixin,
                         ListModelMixin,
                         UpdateModelMixin,
                         RetrieveModelMixin,
                         viewsets.GenericViewSet):
    def get_queryset(self):
        if self.action == 'get' or self.action == 'list':
            return Fields.objects.all()
        elif self.action == 'post':
            return Tags.objects.all()
        return  Tags.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'get' or self.action == 'list':
            return FieldsSerializer
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'post' \
                or self.action == 'read':
            return TagSerializer
        return  TagSerializer

    # 查看所有符合输入的关键词
    # GET /field/?keywords=xxx
    def list(self, request, *args, **kwargs):
        queryset = Fields.objects.filter(field__icontains=request.GET.get('keywords', ''))[:500]
        queryset = self.filter_queryset(queryset)
        selectedfield = []
        for i in queryset:
            selectedfield.append({"field":i.field, "fieldID":i.fieldID})
        questlist = dict()
        questlist['tag'] = selectedfield
        return JsonResponse(questlist)

    # 上传用户领域
    # POST /field/
    # params: {
    #       userID : xxx
    #       field: [
    #           aa,bb,cc
    #       ]
    # }
    def create(self, request, *args, **kwargs):
        #return JsonResponse(request.data, safe=False)
        userid = UserProfile.objects.filter(userID__exact=request.data.get('params').get('userID'))[0]
        for i in request.data.get('params').get("field"):
            field = Fields.objects.filter(fieldID__exact=i.get('fieldID'))[0]
            if Tags.objects.filter(userID__exact=request.data.get('params').get('userID'), fieldID__exact=field.id).exists():
                continue
            tag = Tags()
            tag.userID = userid
            tag.fieldID = field
            tag.save()
        return JsonResponse("OK", safe=False, status=status.HTTP_201_CREATED)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


