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
from .models import Comment
from .serializers import CommentPostSerializer,CommentGetSerializer


#GET /paperDetail/{paperID}
def paperDetail(request,paperID):
    es = Elasticsearch("127.0.0.1:9200")
    ret = es.search(index='papers',
                    body={
                        'query':{
                            'term':{'_id':paperID}
                        }
                    })
    paper_item = ret['hits']['hits'][0]['_source']
    return JsonResponse(paper_item)

#GET /patentDetail/{patentID}
def patentDetail(request,patentID):
    es = Elasticsearch('127.0.0.1:9200')
    # ret = es.search(index='patents',
    #                 body={
    #                     'query': {
    #                         'term': {'_id': patentID}
    #                     }
    #                 })
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
    page = request.GET.get('page',0)
    pageSize = request.GET.get('pageSize',10)
    es = Elasticsearch('127.0.0.1:9200')
    ret = es.search(index='papers',
                    body={
                      "multi_match": {
                        "query": keywords,
                        "fields": [
                          "title",
                          "abstract",
                          "keywords",
                          "fos"
                        ]
                      }
                    })
    ret = ret['hits']['hits']
    paper_list = []
    for item in ret:
        paper_list.append(item['_source'])
    paginator = Paginator(paper_list,pageSize)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(pageSize)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
    papers = papers.object_list
    return JsonResponse(papers,safe=False)

    # json_data = serializers.serialize("json",papers,ensure_ascii=False)
    # return HttpResponse(json_data,content_type='applicaiton/json',charset='utf-8')


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

