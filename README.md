# 🌙 Dream AI

**Dream AI** е уеб приложение изградено с Django, което позволява на потребителите да записват сънищата си и да получават автоматичен AI анализ и визуализация чрез OpenAI.

---

## ✨ Функционалности

- **Запис на сън** — добавяй и съхранявай сънищата си с заглавие и описание
- **AI анализ** — автоматичен психологически анализ на всеки сън чрез GPT-4o Mini
- **AI визуализация** — генериране на уникално изображение за всеки сън чрез DALL·E 3
- **Любими** — маркирай и преглеждай любимите си сънища
- **Дневник** — личен дневник с хронология на всички записани сънища
- **Потребителски профил** — статистики за активност, брой сънища и любими
- **Многоезичност** — поддръжка на множество езици (i18n)
- **Responsive дизайн** — работи на компютър, таблет и телефон

---

## 🛠️ Технологии

| Слой | Технология |
|------|-----------|
| Backend | Django 6.0 |
| База данни | PostgreSQL (`psycopg2`) |
| AI анализ | OpenAI GPT-4o Mini |
| AI изображения | OpenAI DALL·E 3 |
| Frontend | HTML, CSS (custom), Vanilla JS |
| Шрифтове | Google Fonts (Inter, Poppins) |
| Преводи | Django i18n + `googletrans` |

---

## 🚀 Инсталация

### 1. Клонирай проекта

```bash
git clone <repository-url>
cd Analysing_dreams
```

### 2. Създай виртуална среда и инсталирай зависимостите

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настрой environment variables

Създай `.env` файл в основната директория:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgres://user:password@localhost:5432/dream_ai
```

### 4. Приложи миграциите

```bash
python manage.py migrate
```

### 5. Стартирай сървъра

```bash
python manage.py runserver
```

Отвори [http://127.0.0.1:8000](http://127.0.0.1:8000) в браузъра.

---

## 📁 Структура на проекта

```
Analysing_dreams/
├── accounts/          # Регистрация, вход, профил
├── core/              # Начална страница, Dashboard
├── dreams_app/        # Основна логика — сънища, анализ, изображения
│   ├── models.py      # Dream, Favorite, AIAnalysisDailyUsage
│   ├── views.py       # CRUD операции за сънища
│   ├── ai_services.py # Интеграция с OpenAI (анализ + изображения)
│   └── urls.py
├── templates/         # HTML шаблони
├── static/            # CSS и изображения
├── locale/            # Преводи
└── manage.py
```

---

## 🔒 Сигурност

- Защита срещу prompt injection при генериране на изображения
- Автоматично редактиране на чувствително съдържание преди изпращане към OpenAI
- Дневен лимит на AI заявки на потребител (`AIAnalysisDailyUsage`)
- Задължителна автентикация за всички лични страници

---

## 📸 Скрийншотове

> *Добави скрийншотове на приложението тук*

---

## 📄 Лиценз

© 2026 Dream AI. Всички права запазени.
