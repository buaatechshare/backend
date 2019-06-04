# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework import viewsets,status
from rest_framework.status import HTTP_404_NOT_FOUND,HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse

import logging
from django.contrib.auth.models import AnonymousUser


# third-party packges
from elasticsearch import helpers

# my-own packages
from users.views import StandardResultsSetPagination
from .models import Comment,Collection,PaperCheckForm
from .serializers import CommentPostSerializer,CommentGetSerializer,CollectionPostSerializer
from .serializers import PaperCheckPostSerializer,PaperGetSerializer,PatentGetSerializer,PaperCheckFormSerializer
from .es_connect import es
from OAG_APIs.get_Methods import get_paper_details
from backend.settings import PAPER_OFFSET

logger = logging.getLogger()

# #GET /paperDetail/?paperID=xxx
# def paperDetail(request):
#     paperID = request.GET.get('paperID')
#     ret = es.search(index='papers',
#                     body={
#                         'query':{
#                             'term':{'_id':paperID}
#                         }
#                     })
#     if isinstance(request.user,AnonymousUser):
#         user = '未登录用户'
#     else:
#         user = request.user.userID
#     logger.info(
#         'time:%s user_id:%s resource_type:paper resource_id:%s' % (datetime.now,user,paperID)
#     )
#     paper_item = ret['hits']['hits'][0]['_source']
#     if paper_item.get('references') is not None:
#         ref = list()
#         for item in paper_item['references']:
#             try:
#                 ret = es.get(index='papers', id=item)
#             except Exception:
#                 continue
#             ref.append((item,ret['_source'].get('title')))
#         paper_item['references'] = ref
#
#     return JsonResponse(paper_item)



# # GET /patentDetail/?patentID=xxx
# def patentDetail(request):
#     patentID = request.GET.get('patentID')
#     ret = es.get(
#         index='patents',
#         id = patentID,
#     )
#     if isinstance(request.user, AnonymousUser):
#         user = '未登录用户'
#     else:
#         user = request.user.userID
#     logger.info(
#         'time:%s user_id:%s resource_type:patent resource_id:%s' % (
#         datetime.now, user, patentID)
#     )
#     #patent_item = ret['_source']['Patent']
#     patent_item = ret['_source']
#     return JsonResponse(patent_item)

def get_full_paper(paperID):
    ret = es.get(index='papers',id=paperID)
    paper = ret['_source']
    extra_data = get_paper_details(paperID)
    if extra_data is not None:
        for item in extra_data:
            paper[item] = extra_data[item]

    if paper.get('references') is not None:
        ref = list()
        for item in paper['references']:
            try:
                ret = es.get(index='papers', id=item)
            except Exception:
                continue
            ref.append((item, ret['_source'].get('title')))
        paper['references'] = ref
    return paper



class PaperView(APIView):
    # GET /paperDetail/{paperID}/
    def get(self,request,paperID):
        if isinstance(request.user,AnonymousUser):
            user = '未登录用户'
        else:
            user = request.user.userID
        logger.info(
            'userID:%s resType:paper resID:%s' % \
            (user,paperID)
        )
        try:
            paper = get_full_paper(paperID)
        except:
            return Response(status=HTTP_404_NOT_FOUND)
        return JsonResponse(paper)

class PatentView(APIView):
    def get(self,request,patentID):
        if isinstance(request.user,AnonymousUser):
            user = '未登录用户'
        else:
            user = request.user.userID
        logger.info(
            'userID:%s resType:patent resID:%s' % \
            (user,patentID)
        )
        try:
            ret = es.get(
                index='patents',
                id=patentID,
            )
        except:
            return Response(status=HTTP_404_NOT_FOUND)
        # patent = ret['_source']['Patent']
        patent = ret['_source']
        return JsonResponse(patent,safe=False)


#GET /search/papers/?keywords=aaa&page=xxx&pageSize=yyy
def searchPapers(request):
    keywords = request.GET.get('keywords')
    page = int(request.GET.get('page',1))
    pageSize = int(request.GET.get('pageSize',10))
    ret = es.search(
        index="papers",
        body={
            "query": {
                "multi_match": {
                    "query": keywords,
                    "fields": [
                        "title",
                        "author.name"
                    ]
                }
            },
            "size": pageSize,
            "from": (page - 1) * pageSize,
        }
    )
    response = dict()
    response['count'] = ret['hits']['total']['value']
    ret = ret['hits']['hits']
    paper_list = []
    for item in ret:
        try:
            paper_item = get_full_paper(item['_id'])
            paper_item['resourceID'] = paper_item['id']
            paper_list.append(paper_item)
        except:
            continue
    response['results'] = paper_list
    return JsonResponse(response,safe=False)

# GET /search/patents/?keywords=aaa&page=xxx&pageSize=yyy
def searchPatents(request):
    keywords = request.GET.get('keywords')
    page = int(request.GET.get('page',1))
    pageSize = int(request.GET.get('pageSize',10))
    ret = es.search(
        index="patents",
        body={
            "query":{
                "multi_match":{
                    "query":keywords,
                    "fields":[
                        "TI",
                        "AB",
                        "CL"
                    ]
                }
            },
            "size": pageSize,
            "from": (page - 1) * pageSize,
        }
    )
    response = dict()
    response['count'] = ret['hits']['total']['value']
    ret = ret['hits']['hits']

    response['results'] = ret
    return JsonResponse(response, safe=False)


class CommentViewSet(CreateModelMixin,
                     ListModelMixin,
                     viewsets.GenericViewSet):
    """
    create:
        post commmet
    list:
        list all the comments about the resouce
    """
    queryset = Comment.objects.all()
    pagination_class = StandardResultsSetPagination

    #根据请求类型POST/GET/PUT(PATCH)，使用不同的serializer
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentPostSerializer
        return CommentGetSerializer

    def list(self, request, *args, **kwargs):
        queryset = Comment.objects.filter(resourceID=request.query_params.get('resourceID'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CollectionViewSet(CreateModelMixin,
                        DestroyModelMixin,
                        RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    用户收藏
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionPostSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'userID'

    def destroy(self, request, *args, **kwargs):
        userID = kwargs['userID']
        resourceID = request.query_params.get('resourceID')
        instance = Collection.objects.filter(userID=userID,resourceID=resourceID)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    #GET /collections/{userID}/?resType=paper
    def retrieve(self, request, *args, **kwargs):
        resType = request.query_params.get('resType')
        resType = 1 if resType=='paper' else 2
        collectionSet = Collection.objects.filter(userID=kwargs.get('userID'))
        queryset = []

        for item in collectionSet:
            #This item is patent:
            if len(item.resourceID)>=20 and resType==2:
                ret = es.get(index='patents',id=item.resourceID)
                item = dict()
                item['patentID'] = ret['_id']
                # ret = ret['_source']['Patent']
                ret = ret['_source']
                item['patentName'] = ret.get('TI')
                item['rightHolder'] = ret.get('PE')
                item['summary'] = ret.get('AB')
                queryset.append(item)
            #This item is paper
            elif len(item.resourceID)<20 and resType==1:
                try:
                    paper = get_full_paper(item.resourceID)
                    item = dict()
                    item['paperID'] = paper.get('id')
                    item['paperName'] = paper.get('title')
                    item['abstract'] = paper.get('abstract')
                    author_list = []
                    authorID_list = []
                    for author in paper.get('authors'):
                        author_list.append(author.get('name'))
                        authorID_list.append(author.get('id'))
                    item['author'] = author_list
                    item['authorID'] = authorID_list
                except Exception:
                    continue
                queryset.append(item)

        page = self.paginate_queryset(queryset)
        if resType==1:
            if page is not None:
                serializer = PaperGetSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = PaperGetSerializer(queryset, many=True)
            return Response(serializer.data)
        elif resType==2:
            if page is not None:
                serializer = PatentGetSerializer(page,many=True)
                return self.get_paginated_response(serializer.data)
            serializer = PatentGetSerializer(queryset,many=True)
            return Response(serializer.data)

class PaperCheckViewSet(CreateModelMixin,
                        ListModelMixin,
                        UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PaperCheckForm.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return PaperCheckPostSerializer
        return PaperCheckFormSerializer

    #管理员查看所有isCheck=False的表单
    #GET /paperCheck/
    def list(self, request, *args, **kwargs):
        queryset = PaperCheckForm.objects.filter(isCheck=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if serializer.validated_data.get('isPass'):
            formID = serializer.validated_data.get('id')
            user = serializer.validated_data.get('userID')
            title = serializer.validated_data.get('title')
            author = serializer.validated_data.get('author')
            doi = serializer.validated_data.get('doi')
            abstract = serializer.validated_data.get('abstract')
            file = serializer.validated_data.get('file')

            paperEntity = dict()
            paperID = str(int(formID)+PAPER_OFFSET)
            paperEntity['id'] = paperID
            paperEntity['title'] = title
            paperEntity['authors'] = [
                {
                    "name":user.realName,
                    "id":user.expertID
                }
            ]
            paperEntity['abstract'] = abstract
            paperEntity['url'] = file
            paperEntity['doi'] = doi

            #向es.papers插入数据
            try:
                action = {
                    '_index':'papers',
                    '_type':'paper',
                    '_id': paperID,
                    '_source': paperEntity
                }
                a = helpers.bulk(es,[action])
            except Exception:
                return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

            #更新es.authors
            expert = es.get(index='authors',id=user.expertID)
            expert = expert['_source']
            if expert.get('pubs'):
                expert['pubs'].append({"i":paperID,"r":0})

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

