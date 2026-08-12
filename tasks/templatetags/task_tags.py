from django import template
register = template.Library()

@register.filter
def status_badge_class(status_class):
    mapping = {
        'completed': 'bg-success',
        'overdue': 'bg-danger',
        'high-priority': 'bg-warning',
        'medium-priority': 'bg-info',
        'low-priority': 'bg-secondary',
    }
    return mapping.get(status_class, 'bg-light text-dark')


@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    return dictionary.get(key, [])