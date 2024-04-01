from django.contrib import admin
from django.urls import path, include
# Adjusted import statement
from receiver.views import receive_message, get_messages, heatmap_view, get_latest_message, fetch_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('receiver.urls')),
    path('rockblock-receive/', receive_message, name='receive_message'),
    path('rockblock/messages/', get_messages, name='get_messages'),
    path('heatmap/', heatmap_view, name='heatmap'),
    path('latest/message/', get_latest_message, name='latest_msg'),
    path('fetch-history/', fetch_history, name='fetch-history'),

]
