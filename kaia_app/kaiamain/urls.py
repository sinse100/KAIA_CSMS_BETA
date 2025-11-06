"""
URL configuration for kaiamain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import re_path as url
from django.views.static import serve
from django.conf import settings

## (메모) URL 매핑(URL을 어느 views 함수와 매핑 시킬 것인지 결정)을 위한 파일

urlpatterns = [
    path("admin/", admin.site.urls),       ## '/admin/' 이라는 경로는 admin.site.urls 함수와 매핑
    path("",include("eval_service.urls")), ## '/' 이라는 경로는 eval_service 폴더의 urls 폴더로 라우팅    
    url(r'^static/(?P<path>.*)$', serve, {'document_root':settings.STATIC_ROOT}),
]
