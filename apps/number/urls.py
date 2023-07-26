from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('get_user_info', views.get_user_info, name='get_user_info'),
    path('get_data', views.get_data, name='get_data'),
    path('add_data', views.add_data, name='add_data'),
    path('update_data', views.update_data, name='update_data'),
    path('update_UserCount', views.update_UserCount, name='update_UserCount'),

    path('update_user_pk_history', views.update_user_pk_history, name='update_user_pk_history'),
    path('createRoom', views.createRoom, name='createRoom'),
    path('getRoomDetail', views.getRoomDetail, name='getRoomDetail'),
    path('searchRoom', views.searchRoom, name='searchRoom'),
    path('updateRoomDetail', views.updateRoomDetail, name='updateRoomDetail'),
    path('deleteAllRoomIds', views.deleteAllRoomIds, name='deleteAllRoomIds'),
]
