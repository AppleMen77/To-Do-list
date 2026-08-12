function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Тёмная тема
const themeKey = 'todo-theme';
const darkTheme = document.getElementById('dark-theme');
const themeToggle = document.getElementById('theme-toggle');

function applyTheme(theme) {
    if (theme === 'dark') {
        darkTheme.removeAttribute('disabled');
        themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
    } else {
        darkTheme.setAttribute('disabled', '');
        themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i>';
    }
}

const savedTheme = localStorage.getItem(themeKey) || 'light';
applyTheme(savedTheme);

themeToggle?.addEventListener('click', function() {
    const current = darkTheme.hasAttribute('disabled') ? 'light' : 'dark';
    const next = current === 'light' ? 'dark' : 'light';
    localStorage.setItem(themeKey, next);
    applyTheme(next);
});

// Уведомления
if (Notification.permission === 'default') {
    Notification.requestPermission();
}

document.addEventListener('DOMContentLoaded', function() {
    
    // Уведомления о просроченных
    document.querySelectorAll('.status-overdue').forEach(item => {
        const title = item.querySelector('.task-title')?.textContent;
        if (Notification.permission === 'granted' && title) {
            new Notification('Просрочена задача', {body: title});
        }
    });

    // AJAX отметка выполнения
    document.querySelectorAll('.toggle-complete').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = this.dataset.id;
            const item = document.getElementById('item-' + id);
            if (item) item.style.opacity = '0.5';
            
            fetch(`/item/${id}/toggle/`, {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setTimeout(() => location.reload(), 200);
                } else {
                    alert('Задача заблокирована зависимостью');
                }
            });
        });
    });

    // Subtask toggle
    document.querySelectorAll('.subtask-toggle').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = this.dataset.id;
            fetch(`/subtask/${id}/toggle/`, {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setTimeout(() => location.reload(), 200);
                }
            });
        });
    });

    // Drag & Drop
    const list = document.getElementById('sortable-list');
    if (list) {
        new Sortable(list, {
            animation: 200,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            onEnd: function() {
                const order = [...list.querySelectorAll('.task-item')].map(el => el.dataset.id);
                fetch('/update-order/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
                    body: JSON.stringify({order: order}),
                });
            }
        });
    }

    // Быстрое добавление
    document.getElementById('quick-add-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        fetch('/quick-add/', {
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            body: new FormData(this),
        }).then(() => location.reload());
    });

    // Удаление через модальное окно
    const confirmModal = document.getElementById('confirmDeleteModal');
    const confirmText = document.getElementById('confirmDeleteText');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    let pendingForm = null;

    if (confirmModal) {
        const modal = new bootstrap.Modal(confirmModal);

        document.querySelectorAll('.delete-single').forEach(btn => {
            btn.addEventListener('click', function() {
                pendingForm = this.closest('form');
                confirmText.textContent = 'Удалить эту задачу?';
                modal.show();
            });
        });

        confirmBtn.addEventListener('click', function() {
            if (pendingForm) {
                pendingForm.submit();
                pendingForm = null;
            }
            modal.hide();
        });
    }

    // Показать/скрыть опции повторения
    document.querySelectorAll('#id_is_recurring').forEach(cb => {
        cb.addEventListener('change', function() {
            const options = document.querySelector('.recurring-options');
            if (options) options.style.display = this.checked ? 'flex' : 'none';
        });
    });

    // Горячие клавиши
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const modal = document.getElementById('addItemModal');
            if (modal) new bootstrap.Modal(modal).show();
        }
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            document.querySelector('input[name="search"]')?.focus();
        }
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(m => bootstrap.Modal.getInstance(m)?.hide());
        }
    });

});