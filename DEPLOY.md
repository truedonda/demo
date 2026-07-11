# Деплой CozyShop на Render.com

## Что было подготовлено

| Файл | Назначение |
|------|-----------|
| `runtime.txt` | Версия Python 3.13.5 для Render |
| `build.sh` | Скрипт сборки (pip, npm, collectstatic, migrate) |
| `render.yaml` | Blueprint: web-сервис + PostgreSQL + Redis |
| `config/settings/render.py` | Production-настройки для Render |
| `requirements.txt` | Добавлен `dj-database-url` |
| `.gitignore` | `media/` разрешена в Git (фото товаров) |

---

## Шаг 1 — Создать репозиторий на GitHub

1. Зайди на [github.com](https://github.com) → **New repository**
2. Название: `cozyshop` (или любое другое)
3. Visibility: **Private** (рекомендуется)
4. **Не** добавляй README, .gitignore, license — они уже есть
5. Нажми **Create repository**

Затем в терминале VS Code выполни (замени `YOUR_USERNAME` на свой GitHub логин):

```bash
git remote add origin https://github.com/YOUR_USERNAME/cozyshop.git
git branch -M main
git push -u origin main
```

---

## Шаг 2 — Задеплоить на Render

### Вариант A — Автоматически через Blueprint (render.yaml)

1. Зайди на [render.com](https://render.com) → войди / зарегистрируйся
2. Нажми **New** → **Blueprint**
3. Подключи GitHub аккаунт и выбери репозиторий `cozyshop`
4. Render найдёт `render.yaml` и создаст:
   - Web Service (Django + Gunicorn)
   - PostgreSQL база данных (бесплатно)
   - Redis (бесплатно)
5. Нажми **Apply** — деплой запустится автоматически

### Вариант B — Вручную

1. **New** → **Web Service** → подключи репозиторий
2. Настройки:
   - **Runtime:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
3. **Environment Variables** (добавь вручную):

| Переменная | Значение |
|-----------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.render` |
| `DJANGO_SECRET_KEY` | *(сгенерируй случайную строку 50+ символов)* |
| `DJANGO_ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `DATABASE_URL` | *(скопируй из Render PostgreSQL → Connection String)* |
| `REDIS_URL` | *(скопируй из Render Redis → Connection String)* |

4. Создай **PostgreSQL** базу: **New** → **PostgreSQL** → Free plan
5. Создай **Redis**: **New** → **Redis** → Free plan

---

## Шаг 3 — После первого деплоя

### Создать суперпользователя для админки

В Render → твой Web Service → **Shell**:

```bash
python manage.py createsuperuser --settings=config.settings.render
```

### Загрузить данные (если нужно)

Если хочешь перенести данные из локальной SQLite в Render PostgreSQL:

```bash
# Локально — экспорт данных
python manage.py dumpdata --settings=config.settings.local \
  --exclude auth.permission --exclude contenttypes \
  --indent 2 > data_export.json

# Загрузи data_export.json в репозиторий, затем в Render Shell:
python manage.py loaddata data_export.json --settings=config.settings.render
```

---

## Шаг 4 — Проверить сайт

- **Сайт:** `https://your-app-name.onrender.com`
- **Админка:** `https://your-app-name.onrender.com/cozy-admin-2026/`
- **Фото товаров:** раздаются через WhiteNoise по URL `/static/media/products/...`

---

## Важные замечания

### Бесплатный план Render
- Web Service **засыпает** через 15 минут неактивности
- Первый запрос после сна занимает ~30 секунд (cold start)
- PostgreSQL и Redis на бесплатном плане имеют лимиты

### Медиафайлы
- Фото товаров хранятся в `media/` и закоммичены в Git
- При деплое `build.sh` копирует их в `staticfiles/media/`
- WhiteNoise раздаёт их по URL `/static/media/...`
- **Новые фото**, загруженные через админку на Render, **исчезнут** при следующем редеплое
- Для постоянного хранения новых фото — подключи [Cloudinary](https://cloudinary.com) (бесплатный план)

### Обновление сайта
```bash
git add .
git commit -m "Описание изменений"
git push origin main
```
Render автоматически задеплоит новую версию.

---

## Структура настроек

```
config/settings/
├── base.py          # Общие настройки
├── local.py         # Локальная разработка (SQLite, LocMemCache)
├── development.py   # Docker-разработка (PostgreSQL)
├── render.py        # Render.com (PostgreSQL + Redis + WhiteNoise)
└── production.py    # Базовые production-настройки
```
