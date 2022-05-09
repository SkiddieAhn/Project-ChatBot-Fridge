from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    path('', views.home_list, name='home_list'),
    re_path(r'^message', views.message)
]

# 이미지 파일을 제공하기 위한 설정
urlpatterns += static(settings.STATIC_URL,
    document_root=settings.STATIC_ROOT)
'''
urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)
'''