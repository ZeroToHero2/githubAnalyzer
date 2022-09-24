from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
   # path('', include('github.urls'))
    path('', include('testdb.urls'))
]