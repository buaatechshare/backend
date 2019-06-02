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

# my-own packages
from users.views import StandardResultsSetPagination
from .models import Comment,Collection
from .serializers import CommentPostSerializer,CommentGetSerializer,CollectionPostSerializer
from .serializers import PaperGetSerializer,PatentGetSerializer
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
    if paper_item.get('references') is not None:
        ref = list()
        for item in paper_item['references']:
            try:
                ret = es.get(index='papers', id=item)
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
    ret = dict()
    ret['count'] = paginator.count
    ret['results'] = papers
    return JsonResponse(ret,safe=False)

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
            #This item is petent:
            if len(item.resourceID)<25 and resType==2:
                ret = es.get(index='patents',id=item.resourceID)
                item = dict()
                item['patentID'] = ret['_id']
                ret = ret['_source']['Patent']
                item['patentName'] = ret.get('TI')
                item['rightHolder'] = ret.get('PE')
                item['summary'] = ret.get('AB')
                queryset.append(item)
            #This item is paper
            elif len(item.resourceID)>25 and resType==1:
                ret = es.get(index='papers',id=item.resourceID)
                item = dict()
                item['paperID'] = ret['_id']
                ret = ret['_source']
                item['paperName'] = ret.get('title')
                item['abstract'] = ret.get('abstract')
                item['author'] = ret.get('authors')
                item['authorID'] = ret.get('authorID')
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