from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification


@login_required
def notification_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notification_list')


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notification_list')


@login_required
def get_unread_count(request):
    """Get unread notification count (AJAX endpoint)"""
    count = Notification.objects.filter(user=request.user, read=False).count()
    return JsonResponse({'count': count})
