from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "ArenaCampus — Administration"
admin.site.site_title = "ArenaCampus"
admin.site.index_title = "Gestion du tournoi"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tournoi.urls')),
]
