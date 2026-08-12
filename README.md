# 🏢 TaskFlow — Корпоративный ToDo

[![Django](https://img.shields.io/badge/Django-6.0-44B78B?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

**TaskFlow** — корпоративный планировщик задач с геймификацией, командным взаимодействием и аналитикой. Django 6.0 + Bootstrap 5.3.

---

## ✨ Возможности

**Задачи:** приоритеты, сроки, теги, подзадачи с прогрессом, зависимости, повторение, закрепление, Drag & Drop, быстрое добавление.  
**Организация:** рабочие области, списки, умные фильтры (Сегодня / На неделе / Без срока), компактный вид, поиск, корзина с восстановлением.  
**Команда:** назначение исполнителей, комментарии, @упоминания, уведомления, история изменений, роли (Админ / Менеджер / Пользователь).  
**Инструменты:** календарь на месяц, Pomodoro-таймер 25/5 мин, дашборд со статистикой и графиком за 7 дней.  
**Геймификация:** XP за задачи (+5 создание, +10 выполнение), уровни, ежедневная серия, достижения.  
**Интерфейс:** тёмная и светлая темы (Stone + Zinc), адаптивность, анимации, Font Awesome 6.5, админ-панель Django Unfold.

---

## 🚀 Установка

```bash
git clone https://github.com/AppleMen77/To-Do-list.git
cd To-Do-list
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Открыть главную страницу или админ-панель по адресу из консоли.

---

#### ⚙️Стек
Django 6.0 · Bootstrap 5.3 · Font Awesome 6.5 · SortableJS · Django Unfold · SQLite

#### 🎮 Геймификация
+5 XP за создание задачи · +10 XP за выполнение · Уровень каждые 100 XP · Достижения: Первая задача, Продуктивный, Чистый список

#### 🔐 Роли
Администратор — полный доступ · Менеджер — назначение задач и статистика · Пользователь — только свои задачи

---


## 💬 Обратная связь

Нашли баг или есть идея? [Создайте issue](https://github.com/AppleMen77/To-Do-list/issues)

---

## ⭐ Поддержка

Если проект оказался полезным — поставьте звёздочку!

---

#### 📝 Лицензия
Copyright © 2026 AppleMen77. Все права защищены.
