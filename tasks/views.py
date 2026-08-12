import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import (
    Workspace, TodoList, TodoItem, SubTask, Tag,
    UserProfile, Achievement, ActivityLog, Comment, Notification,
    add_xp, check_achievements
)
from .forms import (
    WorkspaceForm, TodoListForm, TodoItemForm, QuickAddForm,
    SubTaskForm, TagForm, CommentForm
)
from django_ratelimit.decorators import ratelimit


# ==================== ГЛАВНАЯ С ПЕРЕКЛЮЧЕНИЕМ ОБЛАСТЕЙ ====================

@login_required
def task_list(request):
    workspace_id = request.GET.get('workspace', '')
    view_mode = request.GET.get('view', 'list')  # list, compact, calendar
    smart_filter = request.GET.get('smart', '')  # today, week, no_deadline

    # Рабочая область
    if workspace_id:
        workspace = get_object_or_404(Workspace, pk=workspace_id, owner=request.user)
        items = TodoItem.objects.filter(user=request.user, workspace=workspace, is_deleted=False)
    else:
        workspace = None
        items = TodoItem.objects.filter(user=request.user, is_deleted=False)

    items = items.select_related('todo_list', 'workspace', 'assigned_to', 'depends_on')
    items = items.prefetch_related('tags', 'subtasks', 'comments')

    # Умные фильтры
    now = timezone.now()
    if smart_filter == 'today':
        items = items.filter(deadline__date=now.date())
    elif smart_filter == 'week':
        week_end = now + timedelta(days=7)
        items = items.filter(deadline__date__gte=now.date(), deadline__date__lte=week_end.date())
    elif smart_filter == 'no_deadline':
        items = items.filter(deadline__isnull=True)

    # Обычные фильтры
    filter_param = request.GET.get('filter', 'all')
    if filter_param == 'active':
        items = items.filter(completed=False)
    elif filter_param == 'completed':
        items = items.filter(completed=True)
    elif filter_param == 'overdue':
        items = items.filter(completed=False, deadline__lt=now)

    # Теги
    tag_filter = request.GET.get('tag', '')
    if tag_filter:
        items = items.filter(tags__id=tag_filter)

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(title__icontains=search_query)

    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    allowed = ['-created_at', 'created_at', 'deadline', '-deadline', 'priority', '-priority', 'order']
    if sort_by in allowed:
        items = items.order_by('-is_pinned', sort_by)
    else:
        items = items.order_by('-is_pinned', '-created_at')

    # Формы
    quick_form = QuickAddForm()
    item_form = TodoItemForm(user=request.user, workspace=workspace)
    subtask_form = SubTaskForm()
    tag_form = TagForm()
    workspace_form = WorkspaceForm()
    comment_form = CommentForm()

    # Счётчики и прогресс
    base = items
    total = base.count()
    completed_count = base.filter(completed=True).count()
    progress = int((completed_count / total * 100)) if total > 0 else 0

    counts = {
        'all': total,
        'active': base.filter(completed=False).count(),
        'completed': completed_count,
        'overdue': base.filter(completed=False, deadline__lt=now).count(),
    }

    # Данные для геймификации
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    achievements = request.user.achievements.all()
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    context = {
        'items': items,
        'workspaces': Workspace.objects.filter(owner=request.user),
        'current_workspace': workspace,
        'lists': TodoList.objects.filter(user=request.user),
        'quick_form': quick_form,
        'item_form': item_form,
        'subtask_form': subtask_form,
        'tag_form': tag_form,
        'workspace_form': workspace_form,
        'comment_form': comment_form,
        'current_filter': filter_param,
        'current_sort': sort_by,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'smart_filter': smart_filter,
        'view_mode': view_mode,
        'counts': counts,
        'progress': progress,
        'tags': Tag.objects.filter(user=request.user),
        'profile': profile,
        'achievements': achievements,
        'notifications': notifications,
    }
    return render(request, 'tasks/task_list.html', context)


# ==================== КАЛЕНДАРЬ ====================

@login_required
def calendar_view(request):
    workspace_id = request.GET.get('workspace', '')
    if workspace_id:
        items = TodoItem.objects.filter(user=request.user, workspace_id=workspace_id, is_deleted=False, deadline__isnull=False)
    else:
        items = TodoItem.objects.filter(user=request.user, is_deleted=False, deadline__isnull=False)

    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    import calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Предыдущий и следующий месяц
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    tasks_by_day = {}
    for item in items:
        if item.deadline.month == month and item.deadline.year == year:
            day = item.deadline.day
            tasks_by_day.setdefault(day, []).append(item)

    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': month_name,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'tasks_by_day': tasks_by_day,
        'workspaces': Workspace.objects.filter(owner=request.user),
        'current_workspace': workspace_id,
    }
    return render(request, 'tasks/calendar.html', context)


# ==================== CRUD ЗАДАЧ ====================

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', block=True)
def item_create(request):
    form = TodoItemForm(request.POST, user=request.user)
    if form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        workspace_id = request.POST.get('workspace')
        if workspace_id:
            item.workspace_id = workspace_id
        item.save()
        form.save_m2m()
        add_xp(request.user, 5)
        check_achievements(request.user)
    return redirect('task_list')


@login_required
def item_edit(request, pk):
    item = get_object_or_404(TodoItem, pk=pk, user=request.user, is_deleted=False)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(user=request.user, task=item, action='updated', description='Задача обновлена')
            return redirect('task_list')
    else:
        form = TodoItemForm(instance=item, user=request.user)
    comments = item.comments.all()
    activity = item.activity_logs.all()[:20]
    return render(request, 'tasks/task_form.html', {
        'form': form, 'item': item, 'comments': comments,
        'activity': activity, 'comment_form': CommentForm()
    })


@login_required
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    item.is_deleted = True
    item.save()
    ActivityLog.objects.create(user=request.user, task=item, action='deleted', description='Задача удалена в корзину')
    return redirect('task_list')


@login_required
@require_POST
def item_restore(request, pk):
    item = get_object_or_404(TodoItem, pk=pk, user=request.user, is_deleted=True)
    item.is_deleted = False
    item.save()
    return redirect('task_list')


@login_required
@require_POST
def item_permanent_delete(request, pk):
    get_object_or_404(TodoItem, pk=pk, user=request.user, is_deleted=True).delete()
    return redirect('task_list')


@login_required
def trash_view(request):
    items = TodoItem.objects.filter(user=request.user, is_deleted=True)
    return render(request, 'tasks/trash.html', {'items': items})


@login_required
@require_POST
def clear_completed(request):
    TodoItem.objects.filter(user=request.user, completed=True, is_deleted=False).update(is_deleted=True)
    return redirect('task_list')


# ==================== AJAX ====================

@login_required
@require_POST
@ratelimit(key='user', rate='30/m', block=True)
def toggle_complete(request, pk):
    item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    if item.is_blocked:
        return JsonResponse({'success': False, 'error': 'Задача заблокирована зависимостью'}, status=400)
    item.completed = not item.completed
    item.save()
    if item.completed:
        add_xp(request.user, 10)
        check_achievements(request.user)
        ActivityLog.objects.create(user=request.user, task=item, action='completed', description='Задача выполнена')
    return JsonResponse({'success': True, 'completed': item.completed, 'status_class': item.status_class})


@login_required
@require_POST
def update_order(request):
    data = json.loads(request.body)
    with transaction.atomic():
        for index, item_id in enumerate(data.get('order', [])):
            TodoItem.objects.filter(pk=item_id, user=request.user).update(order=index)
    return JsonResponse({'success': True})


@login_required
@ratelimit(key='user', rate='5/m', block=True)
def quick_add(request)
    form = QuickAddForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        add_xp(request.user, 5)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


# ==================== ПОДЗАДАЧИ ====================

@login_required
@require_POST
def subtask_add(request, item_id):
    item = get_object_or_404(TodoItem, pk=item_id, user=request.user)
    form = SubTaskForm(request.POST)
    if form.is_valid():
        sub = form.save(commit=False)
        sub.todo_item = item
        sub.save()
    return redirect('task_list')


@login_required
@require_POST
def subtask_toggle(request, subtask_id):
    sub = get_object_or_404(SubTask, pk=subtask_id, todo_item__user=request.user)
    sub.completed = not sub.completed
    sub.save()
    return JsonResponse({'success': True, 'completed': sub.completed, 'progress': sub.todo_item.subtask_progress})


@login_required
@require_POST
def subtask_delete(request, subtask_id):
    sub = get_object_or_404(SubTask, pk=subtask_id, todo_item__user=request.user)
    sub.delete()
    return redirect('task_list')


# ==================== СПИСКИ ====================

@login_required
def list_create(request):
    if request.method == 'POST':
        form = TodoListForm(request.POST)
        if form.is_valid():
            lst = form.save(commit=False)
            lst.user = request.user
            lst.save()
    return redirect('task_list')


@login_required
@require_POST
def list_delete(request, pk):
    get_object_or_404(TodoList, pk=pk, user=request.user).delete()
    return redirect('task_list')


# ==================== ТЕГИ ====================

@login_required
@require_POST
def tag_create(request):
    form = TagForm(request.POST)
    if form.is_valid():
        tag = form.save(commit=False)
        tag.user = request.user
        tag.save()
    return redirect('task_list')


@login_required
@require_POST
def tag_delete(request, pk):
    get_object_or_404(Tag, pk=pk, user=request.user).delete()
    return redirect('task_list')


# ==================== ОБЛАСТИ ====================

@login_required
@require_POST
def workspace_create(request):
    form = WorkspaceForm(request.POST)
    if form.is_valid():
        ws = form.save(commit=False)
        ws.owner = request.user
        ws.save()
    return redirect('task_list')


@login_required
@require_POST
def workspace_delete(request, pk):
    get_object_or_404(Workspace, pk=pk, owner=request.user).delete()
    return redirect('task_list')


# ==================== КОММЕНТАРИИ ====================

@login_required
@require_POST
@ratelimit(key='user', rate='20/m', block=True)
def comment_add(request, item_id):
    item = get_object_or_404(TodoItem, pk=item_id, user=request.user)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = item
        comment.user = request.user
        comment.save()

        # Поиск упоминаний @username
        import re
        mentions = re.findall(r'@(\w+)', comment.text)
        for username in mentions:
            try:
                mentioned_user = User.objects.get(username=username)
                comment.mentions.add(mentioned_user)
                Notification.objects.create(
                    user=mentioned_user,
                    message=f'{request.user.username} упомянул вас в задаче "{item.title}"',
                    url=f'/item/{item.id}/edit/'
                )
            except User.DoesNotExist:
                pass
    return redirect('task_list')


# ==================== УВЕДОМЛЕНИЯ ====================

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'tasks/notifications.html', {'notifications': notifications})


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'success': True})


# ==================== ДАШБОРД (СТАТИСТИКА) ====================

@login_required
def dashboard_view(request):
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    achievements = request.user.achievements.all()

    total_items = TodoItem.objects.filter(user=request.user, is_deleted=False).count()
    completed_items = TodoItem.objects.filter(user=request.user, completed=True, is_deleted=False).count()
    overdue_items = TodoItem.objects.filter(user=request.user, completed=False, is_deleted=False, deadline__lt=timezone.now()).count()

    # Статистика по дням (последние 7 дней)
    stats = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        count = TodoItem.objects.filter(user=request.user, completed=True, updated_at__date=day).count()
        stats.append({'day': day.strftime('%d.%m'), 'count': count})

    context = {
        'profile': profile,
        'achievements': achievements,
        'total_items': total_items,
        'completed_items': completed_items,
        'overdue_items': overdue_items,
        'stats': stats,
    }
    return render(request, 'tasks/dashboard.html', context)


# ==================== POMODORO ====================

@login_required
def pomodoro_view(request, pk):
    item = get_object_or_404(TodoItem, pk=pk, user=request.user)
    return render(request, 'tasks/pomodoro.html', {'item': item})