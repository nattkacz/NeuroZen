from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from core.forms import UserRegisterForm
from core.models import Task, DailyQuote, MoodEntry
from datetime import date



def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    tasks_today = Task.objects.filter(
        category__user=user,
        status='todo',
        due_date=date.today()
    )
    quote = DailyQuote.objects.filter(is_active=True).order_by('?').first()
    mood_entry = MoodEntry.objects.filter(user=user, date=date.today())\
                                   .order_by('-time').first()

    return render(request, 'core/dashboard.html', {
        'tasks_count': tasks_today.count(),
        'quote': quote,
        'mood_entry': mood_entry,
    })