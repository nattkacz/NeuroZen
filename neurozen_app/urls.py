
from django.contrib import admin
from django.urls import path
from core import views

app_name = 'core'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

]
