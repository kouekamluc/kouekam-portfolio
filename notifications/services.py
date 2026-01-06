from django.utils import timezone
from datetime import timedelta
from .models import Notification
from productivity.models import Task, Habit, Goal
from academic.models import StudySession


def create_task_due_notifications():
    """Create notifications for tasks due in the next 24 hours"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    tasks_due = Task.objects.filter(
        due_date__lte=tomorrow,
        due_date__gte=timezone.now().date(),
        status__in=['todo', 'in_progress']
    )
    
    for task in tasks_due:
        Notification.objects.get_or_create(
            user=task.user,
            type='task_due',
            title=f'Task Due: {task.title}',
            message=f'Your task "{task.title}" is due on {task.due_date}',
            related_url=f'/productivity/tasks/{task.id}/update/',
            defaults={'read': False}
        )


def create_habit_reminder_notifications():
    """Create notifications for habits that haven't been completed today"""
    today = timezone.now().date()
    habits = Habit.objects.filter(
        frequency='daily',
        last_completed_date__lt=today
    )
    
    for habit in habits:
        Notification.objects.get_or_create(
            user=habit.user,
            type='habit_reminder',
            title=f'Habit Reminder: {habit.name}',
            message=f'Don\'t forget to complete your habit "{habit.name}" today!',
            related_url=f'/productivity/habits/{habit.id}/track/',
            defaults={'read': False}
        )


def create_goal_milestone_notifications():
    """Create notifications for goals that have reached milestones"""
    goals = Goal.objects.filter(progress__gte=25, progress__lt=100)
    
    milestone_points = [25, 50, 75, 90]
    for goal in goals:
        for milestone in milestone_points:
            if goal.progress >= milestone and goal.progress < milestone + 5:
                Notification.objects.get_or_create(
                    user=goal.user,
                    type='goal_milestone',
                    title=f'Goal Milestone: {goal.title}',
                    message=f'Congratulations! You\'ve reached {milestone}% progress on "{goal.title}"',
                    related_url=f'/productivity/goals/{goal.id}/update/',
                    defaults={'read': False}
                )
                break


def create_study_reminder_notifications():
    """Create notifications for users who haven't studied in 2+ days"""
    two_days_ago = timezone.now().date() - timedelta(days=2)
    
    # Get users who have courses but no recent study sessions
    from academic.models import Course
    from django.db.models import Q
    
    users_with_courses = Course.objects.filter(
        status='ongoing'
    ).values_list('user', flat=True).distinct()
    
    for user_id in users_with_courses:
        recent_sessions = StudySession.objects.filter(
            course__user_id=user_id,
            date__gte=two_days_ago
        ).exists()
        
        if not recent_sessions:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            Notification.objects.get_or_create(
                user=user,
                type='study_reminder',
                title='Study Reminder',
                message='You haven\'t logged a study session in 2+ days. Keep up the momentum!',
                related_url='/academic/dashboard/',
                defaults={'read': False}
            )


def create_all_notifications():
    """Create all types of notifications"""
    create_task_due_notifications()
    create_habit_reminder_notifications()
    create_goal_milestone_notifications()
    create_study_reminder_notifications()

