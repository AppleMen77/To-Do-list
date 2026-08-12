from django.urls import path
from . import views

urlpatterns = [
    # Главная и календарь
    path('', views.task_list, name='task_list'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('dashboard/', views.dashboard_view, name='dashboard_view'),

    # Задачи CRUD
    path('item/create/', views.item_create, name='item_create'),
    path('item/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('item/<int:pk>/restore/', views.item_restore, name='item_restore'),
    path('item/<int:pk>/permanent-delete/', views.item_permanent_delete, name='item_permanent_delete'),
    path('item/<int:pk>/toggle/', views.toggle_complete, name='toggle_complete'),
    path('item/<int:pk>/pomodoro/', views.pomodoro_view, name='pomodoro_view'),

    # AJAX
    path('update-order/', views.update_order, name='update_order'),
    path('quick-add/', views.quick_add, name='quick_add'),
    path('clear-completed/', views.clear_completed, name='clear_completed'),

    # Подзадачи
    path('subtask/<int:item_id>/add/', views.subtask_add, name='subtask_add'),
    path('subtask/<int:subtask_id>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    path('subtask/<int:subtask_id>/delete/', views.subtask_delete, name='subtask_delete'),

    # Списки, теги, области
    path('list/create/', views.list_create, name='list_create'),
    path('list/<int:pk>/delete/', views.list_delete, name='list_delete'),
    path('tag/create/', views.tag_create, name='tag_create'),
    path('tag/<int:pk>/delete/', views.tag_delete, name='tag_delete'),
    path('workspace/create/', views.workspace_create, name='workspace_create'),
    path('workspace/<int:pk>/delete/', views.workspace_delete, name='workspace_delete'),

    # Комментарии
    path('item/<int:item_id>/comment/', views.comment_add, name='comment_add'),

    # Корзина и уведомления
    path('trash/', views.trash_view, name='trash_view'),
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
]