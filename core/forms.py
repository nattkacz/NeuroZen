from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from core.models import Category, Task, MoodEntry, Rewards

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class   TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'points']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None and 'category' in self.fields:
            self.fields['category'].queryset = Category.objects.filter(user=user, is_active=True)


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'notes', 'water_intake', 'exercised', 'diet_summary']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'diet_summary': forms.Textarea(attrs={'rows': 2}),
        }


class RewardForm(forms.ModelForm):
    class Meta:
        model = Rewards
        fields = ['title', 'description', 'points']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'focus_time', 'break_time', 'daily_goal',
            'enable_notifications', 'enable_sound',
            'reminder_frequency',
            'preferred_working_hours_start', 'preferred_working_hours_end',
        ]