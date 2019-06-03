# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import JsonResponse,HttpResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core import serializers
# third-party packges
from elasticsearch import Elasticsearch
import  elasticsearch_dsl
from elasticsearch_dsl import search

from random import *

# my-own packages
from users.views import StandardResultsSetPagination
from users.models import Fields, Tags
from .models import Comment,Collection
from .serializers import CommentPostSerializer,CommentGetSerializer,CollectionPostSerializer
from .es_connect import es

#GET /paperDetail/{paperID}/
def paperDetail(request,paperID):
    ret = es.search(index='papers',
                    body={
                        'query':{
                            'term':{'_id':paperID}
                        }
                    })
    paper_item = ret['hits']['hits'][0]['_source']
    if paper_item['references']:
        ref = list()
        for item in paper_item['references']:
            try:
                ret = es.get(index='papers', id="f655a070-0da7-46d6-b95b-6b6c9d20f265")
            except Exception:
                continue
            ref.append((item,ret['_source'].get('title')))
        paper_item['references'] = ref

    return JsonResponse(paper_item)

#GET /patentDetail/{patentID}/
def patentDetail(request,patentID):
    ret = es.get(
        index='patents',
        id = patentID,
    )
    patent_item = ret['_source']['Patent']
    return JsonResponse(patent_item)

#DSL QUERY????
#GET /search/papers/?keywords=aaa&page=xxx&pageSize=yyy
def searchPapers(request):
    keywords = request.GET.get('keywords')
    page = request.GET.get('page',1)
    pageSize = request.GET.get('pageSize',10)
    ret = es.search(
        index="papers",
        body={
            "query": {
                "multi_match": {
                    "query": keywords,
                    "fields": [
                        "title",
                        "abstract",
                        "keywords",
                        "fos"
                    ]
                }
            }
        }
    )
    # 1.将所有内容直接返回
    # paper_list = ret['hits']['hits']
    # 2.将结果整理后返回
    ret = ret['hits']['hits']
    paper_list = []
    for item in ret:
        paper_item = dict()
        paper_item['type'] = item['_type']
        paper_item['id'] = item['_id']
        paper_item['citation'] = item['_source'].get('n_citaion')
        paper_item['author'] = item['_source'].get('authors')
        paper_item['paperName'] = item['_source'].get('title')
        paper_item['abstract'] = item['_source'].get('abstract')
        paper_list.append(paper_item)

    paginator = Paginator(paper_list,pageSize)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(pageSize)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
    papers = papers.object_list
    return JsonResponse(paper_list,safe=False)

    # json_data = serializers.serialize("json",papers,ensure_ascii=False)
    # return HttpResponse(json_data,content_type='applicaiton/json',charset='utf-8')

# GET /search/patents/?keywords=aaa&page=xxx&pageSize=yyy
def searchPatents(request):
    keywords = request.GET.get('keywords')
    page = request.GET.get('page',0)
    pageSize = request.GET.get('pageSize',10)
    ret = es.search(
        index="patents",
        body={
            "query":{
                "multi_match":{
                    "query":keywords,
                    "fields":[
                        "Patent.TI",
                        "Patent.AB",
                        "Patent.CL"
                    ]
                }
            }
        }
    )
    ret = ret['hits']['hits']
    return JsonResponse(ret,safe=False)

# class PaperViewSet(RetrieveModelMixin,
#                    #ListModelMixin,
#                    viewsets.GenericViewSet):
#     """
#     retrieve:
#         根据resourceID获取对应的论文条目
#     """
#     queryset = Comment.objects.all()
#     pagination_class = StandardResultsSetPagination
#     serializer_class = CommentGetSerializer
#     lookup
#
#     def retrieve(self, request, *args, **kwargs):
#         paperID = kwargs.get('resourceID')
#         es = Elasticsearch("127.0.0.1:9200")
#
#         ret = es.search(index='papers',
#                         body={
#                             "term":{
#                                 '_id':paperID
#                             }
#                         })
#
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)

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
                        viewsets.GenericViewSet):
    """

    """
    queryset = Collection.objects.all()
    serializer_class = CollectionPostSerializer
    lookup_field = 'userID'

    def destroy(self, request, *args, **kwargs):
        userID = kwargs['userID']
        resourceID = request.query_params.get('resourceID')
        instance = Collection.objects.filter(userID=userID,resourceID=resourceID)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)





# 返回推荐论文
# /papersRec/{userID}
def get_rec_paper(request, userID):
    pagenum = int(request.GET['pageNumber'])
    pagesize = int(request.GET['pageSize'])
    userid = str(userID)
    if userid.isspace() or len(userid) == 0:
        pass
    get_field = Tags.objects.filter(userID__exact=userid)
    arr = []
    for i in get_field:
        arr.append({"match":{"fos":str(i.field)}})
    ret = es.search(
        index="papers",
        body={
            "query": {
                "bool": {
                    "minimum_should_match":1,
                    "should": arr
                }
            },
            "size": pagesize,
            "from": (pagenum-1)*pagesize,
        }
    )
    ret = ret['hits']['hits']
    paper_list = []
    for item in ret:
        paper_item = dict()
        paper_item['type'] = item['_type']
        paper_item['id'] = item['_id']
        paper_item['citation'] = item['_source'].get('n_citaion')
        paper_item['author'] = item['_source'].get('authors')
        paper_item['paperName'] = item['_source'].get('title')
        paper_item['abstract'] = item['_source'].get('abstract')
        #paper_item['fos'] = item['_source'].get('fos')
        paper_list.append(paper_item)
    return JsonResponse(paper_list, safe=False)


# 返回推荐专利
# /patentsRec/{userID}
def get_rec_patent(request, userID):
    pagenum = int(request.GET['pageNumber'])
    pagesize = int(request.GET['pageSize'])
    userid = str(userID)
    arr = []
    if userid.isspace() or len(userid) == 0:
        seed(datetime.now())
        con = Fields.objects.latest('id').id
        rand_ids = sample(range(1, con), 100)
        get_field = Fields.objects.filter(id__in=rand_ids)
        for i in get_field:
            if i.type == "paper":
                continue
            arr.append({"match_phrase_prefix": {"Patent.IC": {"query":i.fieldID, "max_expansions": 10}}})
        #return JsonResponse(arr , safe=False)
    else:
        get_field = Tags.objects.filter(userID__exact=userid)
        for i in get_field:
            if i.fieldID.type == "paper":
                continue
            arr.append({"match_phrase_prefix": {"Patent.IC": {"query":i.fieldID.fieldID, "max_expansions": 10}}})
    ret = es.search(
        index="patents",
        body={
            "query": {
                "bool": {
                    "minimum_should_match": 1,
                    "should": arr
                }
            },
            "size": pagesize,
            "from": (pagenum - 1) * pagesize,
        }
    )
    ret = ret['hits']['hits']
    paper_list = []
    con = len(ret)
    for item in ret:
        paper_item = dict()
        paper_item['patentName'] = item['_source']['Patent'].get('TI')
        paper_item['summary'] = item['_source']['Patent'].get('AB')
        paper_item['resourceID'] = item['_id']
        paper_list.append(paper_item)
    ret = dict()
    ret['count'] = con
    ret['results'] = paper_list
    return JsonResponse(ret, safe=False)


'''
ret = ret['hits']['hits']
    paper_list = []
    for item in ret:
        paper_item = dict()
        paper_item['type'] = item['_type']
        paper_item['id'] = item['_id']
        paper_item['citation'] = item['_source'].get('n_citaion')
        paper_item['author'] = item['_source'].get('authors')
        paper_item['paperName'] = item['_source'].get('title')
        paper_item['abstract'] = item['_source'].get('abstract')
        paper_list.append(paper_item)

    paginator = Paginator(paper_list,pageSize)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(pageSize)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
    papers = papers.object_list
    ret = dict()
    ret['count'] = paginator.count
    ret['results'] = papers
    return JsonResponse(ret,safe=False)
'''