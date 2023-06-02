from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
    path('get_data',views.get_data,name='get_data'),
    path('add_data',views.add_data,name='add_data'),
    path('update_data',views.update_data,name='update_data'),
]
