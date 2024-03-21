from django.contrib import admin
from django.urls import path, include
from receiver.views import receive_message, get_messages  # Adjusted import statement

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('receiver.urls')),
    path('rockblock-receive/', receive_message, name='receive_message'),
    path('rockblock/messages/', get_messages, name='get_messages'),

]
