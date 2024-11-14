from django.contrib import admin
from django.urls import path
from skripsi import views
from summarize.views import summarize_from_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summarize_from_url/', summarize_from_url, name='summarize_from_url'),
    path('', views.index, name='index'),
]
