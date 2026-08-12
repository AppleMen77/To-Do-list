import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tasks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    "SITE_TITLE": "Корпоративный ToDo",
    "SITE_HEADER": "Панель управления",
    "SITE_URL": "/",
    "SITE_SYMBOL": "task",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "THEME": "light",
    "COLORS": {
        "primary": {
            "50": "#fafaf9",
            "100": "#f5f5f4",
            "200": "#e7e5e4",
            "300": "#d6d3d1",
            "400": "#a8a29e",
            "500": "#78716c",
            "600": "#57534e",
            "700": "#44403c",
            "800": "#292524",
            "900": "#1c1917",
            "950": "#0c0a09",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Управление",
                "items": [
                    {"title": "Пользователи", "icon": "person", "link": "/admin/auth/user/"},
                    {"title": "Группы", "icon": "group", "link": "/admin/auth/group/"},
                ],
            },
            {
                "title": "Задачи",
                "items": [
                    {"title": "Области", "icon": "dashboard", "link": "/admin/tasks/workspace/"},
                    {"title": "Списки", "icon": "list", "link": "/admin/tasks/todolist/"},
                    {"title": "Задачи", "icon": "task", "link": "/admin/tasks/todoitem/"},
                    {"title": "Подзадачи", "icon": "subdirectory_arrow_right", "link": "/admin/tasks/subtask/"},
                    {"title": "Метки", "icon": "tag", "link": "/admin/tasks/tag/"},
                ],
            },
            {
                "title": "Активность",
                "items": [
                    {"title": "Лог действий", "icon": "history", "link": "/admin/tasks/activitylog/"},
                    {"title": "Комментарии", "icon": "comment", "link": "/admin/tasks/comment/"},
                    {"title": "Уведомления", "icon": "notifications", "link": "/admin/tasks/notification/"},
                ],
            },
            {
                "title": "Геймификация",
                "items": [
                    {"title": "Профили", "icon": "person", "link": "/admin/tasks/userprofile/"},
                    {"title": "Достижения", "icon": "emoji_events", "link": "/admin/tasks/achievement/"},
                ],
            },
        ],
    },
}