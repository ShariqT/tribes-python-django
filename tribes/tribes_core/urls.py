from django.urls import path
from tribes_core import views

urlpatterns = [
    path('info', views.show_info),
    path('sub', views.manage_subs, name='sub_url'),
    path('read', views.read_messages, name='read_url')
]