from django.contrib import admin
from django.urls import path, include
from receiver.views import receive_message_2, get_messages, heatmap_view, get_latest_message, login_view, fetch_history_2, buoy_list_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('receiver.urls')),
    path('rockblock-receive-2/', receive_message_2, name='receive_message_2'),
    path('rockblock/messages/', get_messages, name='get_messages'),
    path('heatmap/', heatmap_view, name='heatmap'),
    path('latest/message/', get_latest_message, name='latest_msg'),
    path('fetch-history-2/', fetch_history_2, name='fetch-history'),
    path('login/', login_view, name='check_credentials'),
    path('bouy_id/', buoy_list_api, name='buoy_list_api'),
]
