from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==================== БАЗОВЫЕ МОДЕЛИ ====================

class Workspace(models.Model):
    """Рабочая область (Личное, Работа, Проект X)"""
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')
    color = models.CharField(max_length=7, default='#78716c')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'owner']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Tag(models.Model):
    """Метки/теги"""
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#78716c')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class TodoList(models.Model):
    """Список задач внутри рабочей области"""
    PRIORITY_CHOICES = [(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')]
    name = models.CharField(max_length=255)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='lists', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_lists')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name


class TodoItem(models.Model):
    """Задача"""
    PRIORITY_CHOICES = [(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')]
    RECURRENCE_CHOICES = [
        ('none', 'Не повторяется'),
        ('daily', 'Каждый день'),
        ('weekly', 'Каждую неделю'),
        ('monthly', 'Каждый месяц'),
    ]

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    todo_list = models.ForeignKey(TodoList, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_items')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_items')

    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    deadline = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.IntegerField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='items')

    # Зависимости
    depends_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_tasks')

    # Повторение
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.IntegerField(default=1)

    # Закрепление
    is_pinned = models.BooleanField(default=False)

    # Сортировка и удаление
    order = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', 'order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.completed or not self.deadline:
            return False
        return self.deadline < timezone.now()

    @property
    def status_class(self):
        if self.completed:
            return 'completed'
        if self.is_overdue:
            return 'overdue'
        if self.priority == 3:
            return 'high-priority'
        if self.priority == 2:
            return 'medium-priority'
        return 'low-priority'

    @property
    def subtask_progress(self):
        total = self.subtasks.count()
        if total == 0:
            return None
        done = self.subtasks.filter(completed=True).count()
        return f"{done}/{total}"

    @property
    def is_blocked(self):
        """Заблокирована ли задача зависимостью"""
        if self.depends_on and not self.depends_on.completed:
            return True
        return False

    def complete(self, user=None):
        """Отметить выполненной с проверкой зависимостей"""
        if self.is_blocked:
            return False
        self.completed = True
        self.save()
        if user:
            ActivityLog.objects.create(user=user, task=self, action='completed', description='Задача выполнена')
            add_xp(user, 10)
            check_achievements(user)
        return True

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.user:
            ActivityLog.objects.create(user=self.user, task=self, action='created', description=f'Задача создана: {self.title}')


class SubTask(models.Model):
    """Подзадачи"""
    todo_item = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=500)
    completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title


# ==================== ГЕЙМИФИКАЦИЯ ====================

class UserProfile(models.Model):
    """Профиль с опытом и уровнями"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — Уровень {self.level}"

    def add_xp(self, amount):
        self.xp += amount
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
        self.save()

    def update_streak(self):
        today = timezone.now().date()
        if self.last_active_date == today:
            return
        if self.last_active_date == today - timezone.timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
        self.last_active_date = today
        self.save()


class Achievement(models.Model):
    """Достижения"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    users = models.ManyToManyField(User, related_name='achievements', blank=True)

    def __str__(self):
        return self.name


def add_xp(user, amount):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.add_xp(amount)
    profile.update_streak()


def check_achievements(user):
    """Проверка и выдача достижений"""
    first_task = Achievement.objects.get_or_create(
        name='Первая задача',
        description='Создайте первую задачу',
        icon='fa-solid fa-flag-checkered'
    )[0]
    ten_tasks = Achievement.objects.get_or_create(
        name='Продуктивный',
        description='Выполните 10 задач за день',
        icon='fa-solid fa-rocket'
    )[0]
    clean_slate = Achievement.objects.get_or_create(
        name='Чистый список',
        description='Выполните все активные задачи',
        icon='fa-solid fa-broom'
    )[0]

    if TodoItem.objects.filter(user=user).count() >= 1:
        first_task.users.add(user)

    completed_today = TodoItem.objects.filter(
        user=user, completed=True,
        updated_at__date=timezone.now().date()
    ).count()
    if completed_today >= 10:
        ten_tasks.users.add(user)

    if TodoItem.objects.filter(user=user, completed=False, is_deleted=False).count() == 0:
        clean_slate.users.add(user)


# ==================== АКТИВНОСТЬ И КОММЕНТАРИИ ====================

class ActivityLog(models.Model):
    """История изменений"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} {self.action} — {self.task.title}"


class Comment(models.Model):
    """Комментарии к задаче"""
    task = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    mentions = models.ManyToManyField(User, related_name='mentions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"


# ==================== УВЕДОМЛЕНИЯ ====================

class Notification(models.Model):
    """Уведомления пользователю"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.message[:50]}"


class UserRole(models.Model):
    """Роль пользователя в системе"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('user', 'Пользователь'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role in ['admin', 'manager']