from django.contrib import admin
from django.urls import path, include
# Adjusted import statement
from receiver.views import receive_message, get_messages, heatmap_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('receiver.urls')),
    path('rockblock-receive/', receive_message, name='receive_message'),
    path('rockblock/messages/', get_messages, name='get_messages'),
    path('heatmap/', heatmap_view, name='heatmap'),
]
