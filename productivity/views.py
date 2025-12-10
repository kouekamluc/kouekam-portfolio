from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import Task, Habit, Goal, Document, Timetable, Transaction, Milestone
from .forms import TaskForm, HabitForm, GoalForm, TransactionForm, TimetableForm, DocumentForm, MilestoneForm

@login_required
def productivity_dashboard(request):
    tasks = Task.objects.filter(user=request.user).order_by('due_date', '-priority')[:10]
    habits = Habit.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user)
    
    context = {
        'tasks': tasks,
        'habits': habits,
        'goals': goals,
        'today': timezone.now().date()
    }
    return render(request, 'productivity/dashboard.html', context)

# Task Views
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('due_date', '-priority')
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    return render(request, 'productivity/task_list.html', {'tasks': tasks, 'status_filter': status_filter})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'productivity/task_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'productivity/task_form.html', {'form': form, 'task': task, 'form_type': 'Update'})

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    return render(request, 'productivity/task_confirm_delete.html', {'task': task})

# Habit Views
@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'productivity/habit_list.html', {'habits': habits})

@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit created successfully!')
            return redirect('habit_list')
    else:
        form = HabitForm()
    return render(request, 'productivity/habit_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def habit_track(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = timezone.now().date()
    
    if request.method == 'POST':
        # Check if already completed today
        if habit.last_completed_date and habit.last_completed_date == today:
            messages.info(request, 'Habit already completed today!')
        else:
            # Calculate streak
            if habit.last_completed_date:
                days_diff = (today - habit.last_completed_date).days
                if days_diff == 1:
                    # Consecutive day - increment streak
                    habit.current_streak += 1
                elif days_diff > 1:
                    # Streak broken - reset to 1
                    habit.current_streak = 1
                else:
                    # Same day or future date (shouldn't happen, but handle it)
                    habit.current_streak = max(habit.current_streak, 1)
            else:
                # First time tracking - start streak at 1
                habit.current_streak = 1
            
            habit.last_completed_date = today
            habit.save()
            messages.success(request, f'Habit tracked! Current streak: {habit.current_streak}')
        return redirect('habit_list')
    
    return render(request, 'productivity/habit_track.html', {'habit': habit})

@login_required
def habit_update(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habit updated successfully!')
            return redirect('habit_list')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'productivity/habit_form.html', {'form': form, 'habit': habit, 'form_type': 'Update'})

@login_required
def habit_delete(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('habit_list')
    return render(request, 'productivity/habit_confirm_delete.html', {'habit': habit})

# Goal Views
@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).order_by('-target_date')
    return render(request, 'productivity/goal_list.html', {'goals': goals})

@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Goal created successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm()
    return render(request, 'productivity/goal_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def goal_update(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully!')
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'productivity/goal_form.html', {'form': form, 'goal': goal, 'form_type': 'Update'})

@login_required
def goal_delete(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
        return redirect('goal_list')
    return render(request, 'productivity/goal_confirm_delete.html', {'goal': goal})

@login_required
def milestone_manage(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    milestones = goal.milestones.all()
    
    if request.method == 'POST':
        if 'create' in request.POST:
            form = MilestoneForm(request.POST)
            if form.is_valid():
                milestone = form.save(commit=False)
                milestone.goal = goal
                milestone.save()
                messages.success(request, 'Milestone created!')
                return redirect('milestone_manage', goal_id=goal.id)
        elif 'complete' in request.POST:
            milestone_id = request.POST.get('milestone_id')
            milestone = get_object_or_404(Milestone, id=milestone_id, goal=goal)
            milestone.completed = True
            milestone.completed_date = timezone.now().date()
            milestone.save()
            messages.success(request, 'Milestone completed!')
            return redirect('milestone_manage', goal_id=goal.id)
    else:
        form = MilestoneForm()
    
    return render(request, 'productivity/milestone_manage.html', {'goal': goal, 'milestones': milestones, 'form': form})

# Timetable Views
@login_required
def timetable_list(request):
    timetables = Timetable.objects.filter(user=request.user)
    return render(request, 'productivity/timetable_list.html', {'timetables': timetables})

@login_required
def timetable_create(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.user = request.user
            # Handle schedule_json separately if needed
            schedule_json = request.POST.get('schedule_json', '{}')
            try:
                timetable.schedule_json = json.loads(schedule_json) if schedule_json else {}
            except json.JSONDecodeError:
                timetable.schedule_json = {}
            timetable.save()
            messages.success(request, 'Timetable created successfully!')
            return redirect('timetable_list')
    else:
        form = TimetableForm()
    return render(request, 'productivity/timetable_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def timetable_update(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=timetable)
        if form.is_valid():
            # Handle schedule_json separately if needed
            schedule_json = request.POST.get('schedule_json', '{}')
            try:
                timetable.schedule_json = json.loads(schedule_json) if schedule_json else timetable.schedule_json
            except json.JSONDecodeError:
                pass  # Keep existing schedule_json if invalid
            form.save()
            messages.success(request, 'Timetable updated successfully!')
            return redirect('timetable_list')
    else:
        form = TimetableForm(instance=timetable)
    return render(request, 'productivity/timetable_form.html', {'form': form, 'timetable': timetable, 'form_type': 'Update'})

@login_required
def timetable_delete(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    if request.method == 'POST':
        timetable.delete()
        messages.success(request, 'Timetable deleted successfully!')
        return redirect('timetable_list')
    return render(request, 'productivity/timetable_confirm_delete.html', {'timetable': timetable})

@login_required
def timetable_generator(request):
    if request.method == 'POST':
        schedule_data = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            schedule_data[day] = []
            time_slots = request.POST.getlist(f'{day}_time')
            activities = request.POST.getlist(f'{day}_activity')
            
            for time, activity in zip(time_slots, activities):
                if time and activity:
                    schedule_data[day].append({'time': time, 'activity': activity})
        
        timetable = Timetable.objects.create(
            user=request.user,
            name=request.POST.get('name', 'My Timetable'),
            schedule_json=schedule_data,
            active=True,
        )
        messages.success(request, 'Timetable generated successfully!')
        return redirect('timetable_list')
    
    return render(request, 'productivity/timetable_generator.html')

# Transaction/Finance Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    type_filter = request.GET.get('type')
    if type_filter:
        transactions = transactions.filter(type=type_filter)
    return render(request, 'productivity/transaction_list.html', {'transactions': transactions, 'type_filter': type_filter})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            if not transaction.date:
                transaction.date = timezone.now().date()
            transaction.save()
            messages.success(request, 'Transaction recorded!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(initial={'date': timezone.now().date()})
    return render(request, 'productivity/transaction_form.html', {'form': form, 'form_type': 'Create'})

@login_required
def transaction_update(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'productivity/transaction_form.html', {'form': form, 'transaction': transaction, 'form_type': 'Update'})

@login_required
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    return render(request, 'productivity/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def finance_dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate totals - handle empty querysets
    income_transactions = transactions.filter(type='income')
    expense_transactions = transactions.filter(type='expense')
    
    total_income = sum(float(t.amount) for t in income_transactions) if income_transactions.exists() else Decimal('0.00')
    total_expenses = sum(float(t.amount) for t in expense_transactions) if expense_transactions.exists() else Decimal('0.00')
    balance = total_income - total_expenses
    
    # Category breakdown
    income_by_category = {}
    expense_by_category = {}
    
    for transaction in transactions:
        if transaction.type == 'income':
            income_by_category[transaction.category] = income_by_category.get(transaction.category, 0) + float(transaction.amount)
        else:
            expense_by_category[transaction.category] = expense_by_category.get(transaction.category, 0) + float(transaction.amount)
    
    # Monthly data for charts
    monthly_data = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        if transaction.type == 'income':
            monthly_data[month_key]['income'] += float(transaction.amount)
        else:
            monthly_data[month_key]['expense'] += float(transaction.amount)
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'income_by_category': income_by_category,
        'expense_by_category': expense_by_category,
        'monthly_data': monthly_data,
    }
    return render(request, 'productivity/finance_dashboard.html', context)

# Document Views
@login_required
def document_list(request):
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    category_filter = request.GET.get('category')
    if category_filter:
        documents = documents.filter(category=category_filter)
    return render(request, 'productivity/document_list.html', {'documents': documents, 'category_filter': category_filter})

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'productivity/document_upload.html', {'form': form})

@login_required
def document_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('document_list')
    return render(request, 'productivity/document_confirm_delete.html', {'document': document})
