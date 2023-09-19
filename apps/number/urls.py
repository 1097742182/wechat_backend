from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    # 基础用户信息
    path('get_user_info', views.get_user_info, name='get_user_info'),
    path('get_data', views.get_data, name='get_data'),
    path('get_rank', views.get_rank, name='get_rank'),
    path('get_top20_rank', views.get_top20_rank, name='get_top20_rank'),
    path('add_data', views.add_data, name='add_data'),
    path('update_data', views.update_data, name='update_data'),
    path('update_UserCount', views.update_UserCount, name='update_UserCount'),

    # 房间URL信息
    path('getWaitingRoom', views.getWaitingRoom, name='getWaitingRoom'),
    path('quitWaitingRoom', views.quitWaitingRoom, name='quitWaitingRoom'),
    path('checkWaitingRoom', views.checkWaitingRoom, name='checkWaitingRoom'),
    path('updateWaitingRoom', views.updateWaitingRoom, name='updateWaitingRoom'),

    path('update_user_pk_history', views.update_user_pk_history, name='update_user_pk_history'),
    path('createRoom', views.createRoom, name='createRoom'),
    path('getRoomDetail', views.getRoomDetail, name='getRoomDetail'),
    path('searchRoom', views.searchRoom, name='searchRoom'),
    path('updateRoomDetail', views.updateRoomDetail, name='updateRoomDetail'),
    path('deleteAllRoomIds', views.deleteAllRoomIds, name='deleteAllRoomIds'),
]
