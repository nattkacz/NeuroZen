from django.contrib import admin
from django.urls import path
from core import views
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


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
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
     path('pomodoro/', views.pomodoro_view, name='pomodoro'),
    path('pomodoro/start/', views.start_pomodoro, name='start_pomodoro'),
    path('pomodoro/end/', views.end_pomodoro, name='end_pomodoro'),
    path('pomodoro/history/', views.pomodoro_history, name='pomodoro_history'),
    path('journal/', views.journal_view, name='journal_view'),
    path('journal/history', views.journal_history, name='journal_history'),
    path('journal/<int:pk>/edit/', views.journal_edit, name='journal_edit'),
    path('journal/<int:pk>/delete/', views.journal_delete, name='journal_delete'),
    path('rewards/', views.reward_list, name='reward_list'),
    path('rewards/add/', views.reward_create, name='reward_create'),
    path('rewards/<int:pk>/edit/', views.reward_edit, name='reward_edit'),
    path('rewards/<int:pk>/delete/', views.reward_delete, name='reward_delete'),
    path('rewards/<int:pk>/claim/', views.reward_claim, name='reward_claim'),
    path('summary/', views.daily_summary_ai, name='daily_summary'),
    path('settings/', views.user_settings, name='user_settings'),
    path('settings/password/', PasswordChangeView.as_view(template_name='core/password_change.html',
        success_url=reverse_lazy('user_settings')),
         name='password_change'),
    path('password-reset/', PasswordResetView.as_view(template_name='core/password_reset.html'), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    path('test-email/', views.test_email),

]
