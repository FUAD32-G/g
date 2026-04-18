from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Case, Task
from .forms import CaseForm


# =====================================
# REDIRECT BASED ON ROLE
# =====================================

def redirect_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    role = request.user.profile.role

    if role == 'reception':
        return redirect('reception_dashboard')
    elif role == 'upload1':
        return redirect('upload1_dashboard')
    elif role == 'upload2':
        return redirect('upload2_dashboard')
    elif role == 'submission':
        return redirect('submission_dashboard')
    elif role == 'tax':
        return redirect('tax_dashboard')
    elif role == 'finance':
        return redirect('finance_dashboard')

    return redirect('owner_dashboard')


# =====================================
# COMPLETE TASK
# =====================================

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if task.status != 'done':
        task.status = 'done'
        task.save()  # triggers next task

    return redirect('redirect_dashboard')


# =====================================
# CREATE CASE (RECEPTION ONLY)
# =====================================

@login_required
def create_case(request):
    if request.user.profile.role != 'reception':
        return redirect('redirect_dashboard')

    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reception_dashboard')
    else:
        form = CaseForm()

    return render(request, 'create_case.html', {'form': form})


# =====================================
# RECEPTION DASHBOARD
# =====================================

@login_required
def reception_dashboard(request):
    query = request.GET.get('q')

    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='cv'
    ).order_by('-created_at')

    if query:
        tasks = tasks.filter(case__customer_name__icontains=query)

    notifications = tasks.filter(status='pending').count()

    return render(request, 'reception.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# UPLOAD 1 DASHBOARD
# =====================================

@login_required
def upload1_dashboard(request):
    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='upload_a'
    ).order_by('-created_at')

    notifications = tasks.filter(status='pending').count()

    return render(request, 'upload1.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# UPLOAD 2 DASHBOARD
# =====================================

@login_required
def upload2_dashboard(request):
    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='upload_b'
    ).order_by('-created_at')

    notifications = tasks.filter(status='pending').count()

    return render(request, 'upload2.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# SUBMISSION DASHBOARD
# =====================================

@login_required
def submission_dashboard(request):
    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='submission'
    ).order_by('-created_at')

    notifications = tasks.filter(status='pending').count()

    return render(request, 'submission.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# TAX DASHBOARD
# =====================================

@login_required
def tax_dashboard(request):
    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='tax'
    ).order_by('-created_at')

    notifications = tasks.filter(status='pending').count()

    return render(request, 'tax.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# FINANCE DASHBOARD
# =====================================

@login_required
def finance_dashboard(request):
    tasks = Task.objects.filter(
        assigned_to=request.user,
        task_type='payment'
    ).order_by('-created_at')

    notifications = tasks.filter(status='pending').count()

    return render(request, 'finance.html', {
        'tasks': tasks,
        'notifications': notifications,
        'now': timezone.now()
    })


# =====================================
# OWNER DASHBOARD (MAIN)
# =====================================

@login_required
def main_dashboard(request):
    query = request.GET.get('q')

    cases = Case.objects.all().order_by('-created_at')

    if query:
        cases = cases.filter(customer_name__icontains=query)

    total_cases = Case.objects.count()
    completed_cases = Case.objects.filter(status='completed').count()
    pending_cases = Case.objects.exclude(status='completed').count()
    delayed_cases = Case.objects.filter(deadline__lt=timezone.now()).count()

    # PERFORMANCE
    users = User.objects.all()
    performance = []

    for user in users:
        performance.append({
            'user': user.username,
            'completed': Task.objects.filter(assigned_to=user, status='done').count(),
            'pending': Task.objects.filter(assigned_to=user, status='pending').count()
        })

    notifications = Task.objects.filter(
        assigned_to=request.user,
        status='pending'
    ).count()

    return render(request, 'dashboard.html', {
        'cases': cases,
        'total_cases': total_cases,
        'completed_cases': completed_cases,
        'pending_cases': pending_cases,
        'delayed_cases': delayed_cases,
        'performance': performance,
        'notifications': notifications,
        'now': timezone.now(),
    })