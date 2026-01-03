
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('boran_app.urls')),
    path('consult/', include('consult_app.urls')),
]
