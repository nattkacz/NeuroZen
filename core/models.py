from datetime import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark')
    ])
    font_size = models.CharField(max_length=20, default='medium', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ])
    enable_notifications = models.BooleanField(default=True)
    enable_sound = models.BooleanField(default=True)

    focus_time = models.IntegerField(default=25, help_text='Focus time in minutes')
    break_time = models.IntegerField(default=5, help_text='Break time in minutes')
    daily_goal = models.IntegerField(default=4, help_text='Daily goal for completed tasks')

    total_completed_tasks = models.IntegerField(default=0)
    total_pomodoro_sessions = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    preferred_working_hours_start = models.TimeField(null=True, blank=True)
    preferred_working_hours_end = models.TimeField(null=True, blank=True)
    reminder_frequency = models.CharField(
        max_length=20,
        default='hourly',
        choices=[
            ('15min', 'Every 15 minutes'),
            ('30min', 'Every 30 minutes'),
            ('hourly', 'Every hour'),
            ('daily', 'Once a day')
        ]
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

    def __str__(self):
        return self.username or self.email


    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            Category.create_default_categories(self)


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('study', 'Study'),
        ('personal', 'Personal'),
        ('health', 'Health'),
        ('social', 'Social'),
        ('hobby', 'Hobby'),
        ('self_care', 'Self Care'),
        ('other', 'Other'),
    ]

    DEFAULT_COLORS = {
        'work': '#FF6B6B',
        'study': '#4ECDC4',
        'personal': '#45B7D1',
        'health': '#96CEB4',
        'social': '#FFEEAD',
        'hobby': '#D4A5A5',
        'self_care': '#9B59B6',
        'other': '#95A5A6',
    }

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#95A5A6')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='categories')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @classmethod
    def create_default_categories(cls, user):
        for category_name, _ in cls.CATEGORY_CHOICES:
            cls.objects.create(
                name=category_name,
                color=cls.DEFAULT_COLORS.get(category_name, '#95A5A6'),
                user=user,
                is_default=True,
                is_active=True
            )


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completed_at = models.DateTimeField(null=True, blank=True, help_text='Estimated time in minutes')
    actual_completed_at = models.DateTimeField(null=True, blank=True, help_text='Actual time in minutes')

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class PomodoroSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    duration = models.IntegerField(help_text='Duration in minutes')
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Pomodoro Session ({self.user.username}) - {self.start_time}"


class Rewards(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rewards')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class DailyQuote(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quote[:50]}... - {self.author}"


class BreathingExercise(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    inhale_duration = models.IntegerField(help_text='Duration in seconds')
    hold_duration = models.IntegerField(help_text='Duration in seconds')
    exhale_duration = models.IntegerField(help_text='Duration in seconds')
    cycles = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('very_happy', 'Very Happy'),
        ('happy', 'Happy'),
        ('neutral', 'Neutral'),
        ('sad', 'Sad'),
        ('very_sad', 'Very Sad'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mood_entries')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_mood_display()} - {self.user.username} - {self.date}"