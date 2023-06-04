from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('get_user_info',views.get_user_info,name='get_user_info'),
    path('get_user',views.get_user,name='get_user'),
    path('get_data',views.get_data,name='get_data'),
    path('add_data',views.add_data,name='add_data'),
    path('update_data',views.update_data,name='update_data'),
    path('update_UserCount',views.update_UserCount,name='update_UserCount'),
]
