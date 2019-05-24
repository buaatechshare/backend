"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from users.views import UserViewSet,MessageViewSet

router = DefaultRouter()
#用户注册register
router.register('users',UserViewSet,base_name='users')

#站内信
router.register('messages',MessageViewSet,base_name='messages')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/',include('rest_framework.urls')),
    #用户登录
    path('login/', obtain_jwt_token),
    #router注册的url
    path('',include(router.urls)),
    #drf自带文档管理
    path('docs/',include_docs_urls(title='backend'))
]
