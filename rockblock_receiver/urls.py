from django.contrib import admin
from django.urls import path, include
from receiver.views import receive_message  # Adjusted import statement

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('receiver.urls')),
    path('rockblock-receive/', receive_message, name='receive_message'),
]
