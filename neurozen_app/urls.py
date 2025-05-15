from django.contrib import admin
from django.urls import path
from core import views


app_name = 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/categories/', views.task_categories, name='task_categories'),
    path('tasks/category/<int:pk>/', views.tasks_by_category, name='tasks_by_category'),
    path('pomodoro/', views.pomodoro_view, name='pomodoro'),
    path('pomodoro/start/', views.start_pomodoro, name='start_pomodoro'),
    path('pomodoro/end/', views.end_pomodoro, name='end_pomodoro'),
    path('pomodoro/history/', views.pomodoro_history, name='pomodoro_history'),
]
