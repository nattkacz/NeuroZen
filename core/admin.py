from django.contrib import admin
from .models import (
    User, Category, Task, PomodoroSession,
    Rewards, DailyQuote, BreathingExercise,
    MoodEntry, AISummary
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "points", "total_completed_tasks", "total_pomodoro_sessions", "streak_days")
    list_filter = ("enable_notifications", "enable_sound", "reminder_frequency", "last_active_date")
    search_fields = ("username", "email")
    ordering = ("-points",)
    readonly_fields = ("last_active_date", "total_completed_tasks", "total_pomodoro_sessions", "streak_days")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_display", "user", "is_default", "is_active", "created_at")
    list_filter = ("is_default", "is_active", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("name",)

    def name_display(self, obj):
        return str(obj)
    name_display.short_description = "Category name"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "priority", "status", "due_date", "points", "completed_at")
    list_filter = ("priority", "status", "category", "due_date", "completed_at")
    search_fields = ("title", "description", "user__username")
    ordering = ("due_date",)
    readonly_fields = ("created_at", "completed_at")


@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "task", "start_time", "end_time", "duration", "completed")
    list_filter = ("completed", "start_time")
    search_fields = ("user__username", "task__title")
    ordering = ("-start_time",)


@admin.register(Rewards)
class RewardsAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "points", "is_claimed", "claimed_at", "is_active", "created_at")
    list_filter = ("is_claimed", "is_active", "created_at")
    search_fields = ("title", "description", "user__username")
    ordering = ("-created_at",)


@admin.register(DailyQuote)
class DailyQuoteAdmin(admin.ModelAdmin):
    list_display = ("quote_preview", "author", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("quote", "author")
    ordering = ("-created_at",)

    def quote_preview(self, obj):
        return (obj.quote[:50] + "...") if len(obj.quote) > 50 else obj.quote
    quote_preview.short_description = "Quote"


@admin.register(BreathingExercise)
class BreathingExerciseAdmin(admin.ModelAdmin):
    list_display = ("title", "inhale_duration", "hold_duration", "exhale_duration", "cycles", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    ordering = ("title",)


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "mood", "water_intake", "exercised", "date", "time", "notes_preview")
    list_filter = ("mood", "exercised", "date")
    search_fields = ("user__username", "notes", "diet_summary")
    ordering = ("-date",)

    def notes_preview(self, obj):
        return (obj.notes[:50] + "...") if len(obj.notes) > 50 else obj.notes
    notes_preview.short_description = "Notes"


@admin.register(AISummary)
class AISummaryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "content_preview", "created_at")
    list_filter = ("date",)
    search_fields = ("user__username", "content")
    ordering = ("-date",)

    def content_preview(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Summary"
