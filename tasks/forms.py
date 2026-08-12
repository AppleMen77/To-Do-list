from django import forms
from django.contrib.auth.models import User
from .models import Workspace, TodoList, TodoItem, SubTask, Tag, Comment


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название области'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название метки'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }


class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ['name', 'priority']


class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = [
            'title', 'description', 'priority', 'deadline', 'estimated_minutes',
            'todo_list', 'tags', 'assigned_to', 'depends_on',
            'is_recurring', 'recurrence_type', 'recurrence_interval',
            'is_pinned'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Что нужно сделать?'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Описание'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'estimated_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Минуты'}),
            'todo_list': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'depends_on': forms.Select(attrs={'class': 'form-select'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recurrence_type': forms.Select(attrs={'class': 'form-select'}),
            'recurrence_interval': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Интервал'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        workspace = kwargs.pop('workspace', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['todo_list'].queryset = TodoList.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['depends_on'].queryset = TodoItem.objects.filter(user=user, completed=False)


class QuickAddForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ['title', 'priority']


class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Подзадача...'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Комментарий... Используйте @username для упоминания'}),
        }