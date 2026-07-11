# COZYSHOP — Отчёт об аудите безопасности

> Дата аудита: 2026-06-16  
> Область проверки: весь кодовой базы — Django-представления, модели, шаблоны, настройки, логика корзины/вишлиста, админка, конфигурация Docker

---

## КРИТИЧЕСКИЕ

### 1. Захардкоженный запасной `SECRET_KEY` в `base.py`

**Файл:** [`config/settings/base.py:6`](config/settings/base.py)

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')
```

**Риск:** Если переменная окружения `DJANGO_SECRET_KEY` не задана в продакшене, Django молча использует строку `'change-me-in-production'`. Этот ключ подписывает сессии, CSRF-токены, ссылки для сброса пароля и все подписанные куки. Злоумышленник, знающий это значение, может подделать любой из этих объектов.

**Исправление:**
```python
import sys

_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret:
    if 'runserver' not in sys.argv:
        raise ImproperlyConfigured(
            'Переменная окружения DJANGO_SECRET_KEY не задана.'
        )
    # Разрешить runserver только с локальными настройками
    _secret = 'dev-only-insecure-key-do-not-use-in-production'

SECRET_KEY = _secret
```

---

### 2. Захардкоженные учётные данные базы данных в `base.py`

**Файл:** [`config/settings/base.py:62-70`](config/settings/base.py)

```python
'PASSWORD': os.environ.get('DB_PASSWORD', 'cozyshop'),
'USER':     os.environ.get('DB_USER',     'cozyshop'),
'NAME':     os.environ.get('DB_NAME',     'cozyshop'),
```

**Риск:** Если переменные окружения не заданы, Django подключается к базе данных с общеизвестными учётными данными `cozyshop/cozyshop`. Любой злоумышленник с сетевым доступом к порту БД может пройти аутентификацию.

**Исправление:** Убрать все запасные значения для учётных данных:
```python
'NAME':     os.environ['DB_NAME'],
'USER':     os.environ['DB_USER'],
'PASSWORD': os.environ['DB_PASSWORD'],
'HOST':     os.environ.get('DB_HOST', 'localhost'),
'PORT':     os.environ.get('DB_PORT', '5432'),
```

---

### 3. `SECURE_SSL_REDIRECT = False` в настройках продакшена

**Файл:** [`config/settings/production.py:8`](config/settings/production.py)

```python
SECURE_SSL_REDIRECT = False
```

**Риск:** HTTPS не принудительно применяется на уровне Django. Весь трафик — включая учётные данные для входа, куки сессий, CSRF-токены — может передаваться в открытом виде при неправильной настройке или обходе обратного прокси.

**Исправление:**
```python
SECURE_SSL_REDIRECT = True
```
Если SSL-терминация происходит на прокси (nginx), оставьте `False`, но убедитесь, что nginx принудительно применяет HTTPS с редиректом `301` и прокси устанавливает заголовок `X-Forwarded-Proto: https`.

---

### 4. Открытый редирект через параметр `next` при входе

**Файл:** [`apps/accounts/views.py:36`](apps/accounts/views.py)

```python
next_url = request.POST.get('next') or request.GET.get('next') or reverse('accounts:account')
```

**Риск:** Злоумышленник может создать ссылку вида `/account/login/?next=https://evil.com`, и после успешного входа пользователь будет перенаправлен на внешний сайт. Это классический вектор фишинга.

**Исправление:** Проверить, что `next` является безопасным внутренним URL:
```python
from django.utils.http import url_has_allowed_host_and_scheme

raw_next = request.POST.get('next') or request.GET.get('next') or ''
if url_has_allowed_host_and_scheme(raw_next, allowed_hosts={request.get_host()}):
    next_url = raw_next
else:
    next_url = reverse('accounts:account')
```

---

### 5. Статус оплаты изменяется через неаутентифицированный GET-запрос

**Файл:** [`apps/orders/views.py:82-96`](apps/orders/views.py)

```python
class PaymentSuccessView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.payment_status = Order.PAYMENT_PAID
        order.status = Order.STATUS_CONFIRMED
        order.save(...)
```

**Риск:** Любой, кто знает (или угадывает) PK заказа, может пометить любой заказ как оплаченный, просто перейдя по адресу `/orders/payment/<pk>/success/`. PK заказов — последовательные целые числа, которые тривиально перебираются. Это критическая уязвимость бизнес-логики.

**Исправление:**
1. Использовать криптографически случайный токен в модели `Order` вместо PK в URL оплаты.
2. Проверять оплату на стороне сервера через вебхук реального платёжного шлюза (не GET-ссылку).
3. Как минимум, проверять, что сессия создала этот заказ:

```python
class PaymentSuccessView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Проверить, что сессия создала этот заказ
        if request.session.get('last_order_pk') != order.pk:
            raise PermissionDenied
        ...
```

---

## ВЫСОКИЕ

### 6. Отсутствует ограничение частоты запросов на регистрацию и вход

**Файл:** [`apps/accounts/views.py`](apps/accounts/views.py)

**Риск:** Нет защиты от брутфорса в `LoginView.post()` и `RegisterView.post()`. Злоумышленник может:
- Перечислять действительные имена пользователей через временны́е различия
- Перебирать пароли без блокировки
- Спамить создание аккаунтов (DoS, спам)

**Исправление:** Добавить `django-ratelimit` или `django-axes`:
```python
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LoginView(View):
    ...
```

---

### 7. Перечисление имён пользователей через различные сообщения об ошибках

**Файл:** [`apps/accounts/views.py:66-72`](apps/accounts/views.py)

```python
errors['username'] = 'This username is already taken.'
errors['email'] = 'An account with this email already exists.'
```

**Риск:** Регистрация возвращает различные ошибки для занятого имени пользователя и существующего email. Это позволяет злоумышленнику перечислять действительные имена пользователей и email-адреса.

**Исправление:** Возвращать общее сообщение при ошибках регистрации или использовать паттерн анти-перечисления (всегда показывать «если этот email существует, вы получите подтверждение»).

---

### 8. Отсутствует CSRF-защита в `CartRemoveView` (метод DELETE)

**Файл:** [`apps/cart/views.py:59-72`](apps/cart/views.py)

```python
class CartRemoveView(View):
    def delete(self, request, item_id):
```

**Риск:** Метод `DELETE` отправляется через `fetch()` в шаблоне с `getCsrf()` в заголовках — это правильно. Однако если заголовок `X-CSRFToken` отсутствует (например, при кросс-доменном запросе), Django может не применять CSRF для нестандартных методов в зависимости от конфигурации middleware.

**Исправление:** Изменить на `POST` с переопределением `_method=DELETE` (более совместимо):
```python
class CartRemoveView(View):
    def post(self, request, item_id):  # Использовать POST вместо DELETE
        ...
```
Обновить URL-паттерн и шаблон соответственно.

---

### 9. Фиксация сессии — корзина теряется после входа

**Файл:** [`apps/cart/cart.py:6-8`](apps/cart/cart.py)

```python
if not request.session.session_key:
    request.session.create()
self.session_key = request.session.session_key
```

**Риск:** Ключ сессии корзины создаётся до входа. После входа Django ротирует ID сессии (через `django.contrib.auth.login()`), но записи `CartItem` остаются привязанными к старому ключу сессии. Корзина теряется после входа. Более критично: если ротация сессии отключена, предварительный ключ сессии сохраняется, что позволяет атаки фиксации сессии.

**Исправление:** После входа перенести элементы корзины со старого ключа сессии на новый:
```python
# В LoginView.post(), после login(request, user):
old_key = old_session_key  # сохранить до login()
new_key = request.session.session_key
if old_key and old_key != new_key:
    CartItem.objects.filter(session_key=old_key).update(session_key=new_key)
```

---

### 10. Отсутствует максимальный лимит количества товаров в корзине

**Файл:** [`apps/cart/cart.py:29-30`](apps/cart/cart.py)

```python
def update_quantity(self, item_id, quantity):
    CartItem.objects.filter(...).update(quantity=max(1, quantity))
```

**Риск:** Пользователь может установить количество `2147483647` (максимальный int). Это приводит к тому, что `total_price()` возвращает астрономически большое значение `Decimal`, потенциально переполняя поля отображения, нарушая создание заказов или вызывая DoS через медленные запросы к БД.

**Исправление:**
```python
MAX_QUANTITY = 99
CartItem.objects.filter(...).update(quantity=max(1, min(quantity, MAX_QUANTITY)))
```

---

### 11. Вишлист хранится полностью в сессии — без ограничения размера

**Файл:** [`apps/cart/wishlist.py:10-11`](apps/cart/wishlist.py)

```python
if WISHLIST_SESSION_KEY not in self.session:
    self.session[WISHLIST_SESSION_KEY] = []
self.product_ids = self.session[WISHLIST_SESSION_KEY]
```

**Риск:** Злоумышленник может добавить тысячи ID продуктов в сессию вишлиста, раздувая хранилище сессий (БД или файл). При `SESSION_ENGINE = 'django.contrib.sessions.backends.db'` это создаёт большие строки в БД и медленные запросы.

**Исправление:**
```python
MAX_WISHLIST_SIZE = 100

def add(self, product_id):
    product_id = int(product_id)
    if product_id not in self.product_ids and len(self.product_ids) < MAX_WISHLIST_SIZE:
        self.product_ids.append(product_id)
        self.session.modified = True
```

---

### 12. `SESSION_COOKIE_HTTPONLY` явно не задан

**Файл:** [`config/settings/base.py`](config/settings/base.py)

**Риск:** Django по умолчанию устанавливает `SESSION_COOKIE_HTTPONLY = True`, но это явно не задано. Если будущая версия Django изменит это значение по умолчанию, или разработчик добавит `SESSION_COOKIE_HTTPONLY = False` в другом месте, JavaScript сможет читать куки сессии, что позволит перехватить сессию через XSS.

**Исправление:** Явно задать в `base.py`:
```python
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Должно быть False, чтобы JS мог читать CSRF-токен (HTMX)
```

---

## СРЕДНИЕ

### 13. `CSRF_COOKIE_HTTPONLY` явно не задан — CSRF-токен читается JS (намеренно, но не задокументировано)

**Файл:** [`config/settings/base.py`](config/settings/base.py) / [`templates/base.html:244`](templates/base.html)

```javascript
function getCsrf() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}
```

**Риск:** CSRF-токен читается из куки через JavaScript (требуется для HTMX/fetch). Это намеренно, но означает, что `CSRF_COOKIE_HTTPONLY` должен быть `False`. Это должно быть явно задокументировано и установлено, чтобы избежать случайного «ужесточения», которое сломает сайт.

**Исправление:** Добавить в `base.py`:
```python
CSRF_COOKIE_HTTPONLY = False  # Обязательно: HTMX читает CSRF-токен из куки через JS
```

---

### 14. Отсутствует `@login_required` в `AccountView`

**Файл:** [`apps/accounts/views.py:18-21`](apps/accounts/views.py)

```python
class AccountView(TemplateView):
    def get(self, request, *args, **kwargs):
        ...
        return render(request, 'accounts/account.html')
```

**Риск:** Страница аккаунта доступна неаутентифицированным пользователям (показывает состояние «Гость»). Это сделано намеренно, но нет защиты на случай добавления конфиденциальных данных пользователя в это представление в будущем.

**Исправление:** Если страница аккаунта когда-либо будет показывать личные данные (история заказов, сохранённые адреса), добавить `@login_required`.

---

### 15. `DATA_UPLOAD_MAX_MEMORY_SIZE` установлен в 20 МБ

**Файл:** [`config/settings/base.py:94`](config/settings/base.py)

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 МБ
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 МБ
```

**Риск:** Формы оформления заказа и входа принимают только текстовые данные. Лимит в 20 МБ для POST-тела избыточен для этих эндпоинтов и позволяет DoS-атаки с большим телом запроса.

**Исправление:** Оставить 20 МБ только для загрузки изображений в админке. Для публичных эндпоинтов достаточно стандартного лимита Django (2,5 МБ). Рассмотреть лимиты на уровне представлений или уменьшить глобальный лимит до 2 МБ.

---

### 16. Поле номера телефона не имеет валидации

**Файл:** [`apps/orders/forms.py:17`](apps/orders/forms.py) / [`apps/orders/models.py:30`](apps/orders/models.py)

```python
phone = models.CharField(max_length=30)
```

**Риск:** Нет валидации формата номера телефона. Злоумышленник может отправить произвольные строки (включая HTML/script-теги, SQL-фрагменты или очень длинные строки до 30 символов). Хотя ORM Django предотвращает SQL-инъекции, а шаблоны автоматически экранируют HTML, сырое значение хранится и отображается в админке.

**Исправление:** Добавить валидатор:
```python
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{7,20}$',
    message='Введите корректный номер телефона.'
)
phone = models.CharField(max_length=30, validators=[phone_validator])
```

---

### 17. Итоговая сумма заказа не проверяется на > 0

**Файл:** [`apps/orders/views.py:37`](apps/orders/views.py)

```python
order.total_price = cart.total_price()
```

**Риск:** Итоговая сумма вычисляется из текущей корзины при оформлении заказа. Если цена товара изменится между «добавить в корзину» и «оформить заказ», итог заказа отразит новую цену без предупреждения пользователя. Более критично: нет серверной проверки того, что итог > 0.

**Исправление:** Добавить проверку:
```python
computed_total = cart.total_price()
assert computed_total > 0, "Нельзя создать заказ с нулевой суммой"
order.total_price = computed_total
```

---

### 18. Сжатие изображений молча проглатывает все исключения — уязвимость «image bomb»

**Файл:** [`apps/catalog/models.py:124`](apps/catalog/models.py)

```python
except Exception:
    # Never break a save because of compression failure
    pass
```

**Риск:** Любая ошибка при обработке изображений (включая `MemoryError` от специально созданного изображения — «image bomb») молча игнорируется. Крошечный PNG, разворачивающийся до гигабайт, может исчерпать память сервера.

**Исправление:**
```python
from PIL import Image

Image.MAX_IMAGE_PIXELS = 50_000_000  # Максимум ~50 мегапикселей (добавить на уровне модуля)

# В _compress_image_field:
except Exception as e:
    import logging
    logging.getLogger(__name__).warning('Сжатие изображения не удалось: %s', e)
```

---

### 19. Панель администратора доступна без двухфакторной аутентификации

**Файл:** [`config/urls.py:7`](config/urls.py)

```python
path('admin/', admin.site.urls),
```

**Риск:** Панель Django-admin доступна по стандартному пути `/admin/` только с аутентификацией по логину/паролю. Нет ограничения по IP, нет 2FA, нет нестандартного URL.

**Исправление:**
1. Изменить URL админки на непредсказуемый путь: `path('_internal/manage-2026/', admin.site.urls)`
2. Добавить `django-otp` или `django-two-factor-auth` для 2FA
3. Ограничить доступ к админке по IP в nginx/middleware

---

### 20. `ALLOWED_HOSTS` может быть пустой строкой в продакшене

**Файл:** [`config/settings/production.py:5`](config/settings/production.py)

```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

**Риск:** Если `DJANGO_ALLOWED_HOSTS` не задан, `ALLOWED_HOSTS` становится `['']` — пустой строкой. Django воспринимает это как отсутствие разрешённых хостов, что вызывает `400 Bad Request` для всех запросов. Однако если переменная установлена в `*`, разрешены все хосты (инъекция HTTP Host-заголовка).

**Исправление:**
```python
_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if not _hosts:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS должен быть задан в продакшене.')
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]
```

---

## НИЗКИЕ

### 21. `SESSION_COOKIE_AGE` установлен в 30 дней

**Файл:** [`config/settings/base.py:98`](config/settings/base.py)

```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 дней
```

**Риск:** Сессии сохраняются 30 дней. Если устройство пользователя украдено или токен сессии утёк, у злоумышленника есть 30-дневное окно. Для интернет-магазина с платёжными потоками это дольше, чем необходимо.

**Исправление:** Уменьшить до 7 дней для аутентифицированных сессий или реализовать скользящее истечение:
```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7   # 7 дней
SESSION_SAVE_EVERY_REQUEST = True         # Скользящее истечение
```

---

### 22. Отсутствует заголовок `Content-Security-Policy`

**Файл:** [`config/settings/production.py`](config/settings/production.py)

**Риск:** Заголовок CSP не установлен. Это означает, что любая XSS-уязвимость (например, во внедрённом HTMX-контенте, директивах Alpine `x-html` или будущих ошибках шаблонов) может выполнять произвольные скрипты, красть куки или эксфильтровать данные.

**Исправление:** Добавить `django-csp` или настроить через nginx:
```python
# settings/production.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.tailwindcss.com", "https://unpkg.com", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "https://fonts.googleapis.com", "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "blob:")
```

---

### 23. Директива `x-html` рендерит несанированный HTML

**Файл:** [`templates/partials/navbar.html:186`](templates/partials/navbar.html)

```html
<div x-show="searchResults && !searchLoading" x-html="searchResults" ...></div>
```

**Риск:** `x-html` устанавливает `innerHTML` напрямую. Значение `searchResults` приходит с сервера через fetch `/search/suggest/`. Если шаблон результатов поиска когда-либо выведет неэкранированный пользовательский ввод (например, название товара с `<script>`), он выполнится в браузере. Шаблоны Django автоматически экранируют по умолчанию, но это важно для глубокой защиты.

**Исправление:** Убедиться, что шаблон результатов поиска никогда не использует `{{ value | safe }}` или `{% autoescape off %}`. Добавить комментарий в шаблон:
```html
{# БЕЗОПАСНОСТЬ: Этот шаблон рендерится через x-html (innerHTML). Никогда не используйте |safe здесь. #}
```

---

### 24. Отсутствует `robots.txt` — URL админки и внутренние URL индексируются

**Риск:** Поисковые системы могут индексировать `/admin/`, `/cart/`, `/orders/`, раскрывая структуру URL и потенциально вызывая нежелательные GET-запросы от краулеров.

**Исправление:** Добавить `robots.txt`:
```
User-agent: *
Disallow: /admin/
Disallow: /cart/
Disallow: /orders/
Disallow: /account/
Allow: /
```

---

### 25. `SECURE_BROWSER_XSS_FILTER` устарел

**Файл:** [`config/settings/production.py:18`](config/settings/production.py)

```python
SECURE_BROWSER_XSS_FILTER = True
```

**Риск:** Этот параметр устанавливает заголовок `X-XSS-Protection: 1; mode=block`, который устарел и удалён в современных браузерах. В некоторых старых браузерах он может фактически вводить XSS-уязвимости. Не имеет эффекта в Chrome 78+, Firefox или Safari.

**Исправление:** Удалить этот параметр и полагаться на CSP:
```python
# Удалить: SECURE_BROWSER_XSS_FILTER = True
# Заменить правильным CSP (см. проблему #22)
```

---

### 26. Отсутствует `favicon.ico` — 404 логируется при каждой загрузке страницы

**Файл:** Логи сервера показывают повторяющиеся `404` для `/favicon.ico`

**Риск:** Не является проблемой безопасности как таковой, но каждый ответ 404 раскрывает структуру страницы ошибок Django в режиме разработки и генерирует лишний шум в логах продакшена, потенциально маскируя реальные ошибки.

**Исправление:** Добавить `favicon.ico` в `static/` и раздавать его:
```python
# urls.py
from django.views.generic import RedirectView
path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
```

---

## СВОДНАЯ ТАБЛИЦА

| # | Серьёзность | Проблема | Файл |
|---|-------------|----------|------|
| 1 | 🔴 КРИТИЧЕСКАЯ | Захардкоженный запасной `SECRET_KEY` | `config/settings/base.py` |
| 2 | 🔴 КРИТИЧЕСКАЯ | Захардкоженные учётные данные БД | `config/settings/base.py` |
| 3 | 🔴 КРИТИЧЕСКАЯ | `SECURE_SSL_REDIRECT = False` в продакшене | `config/settings/production.py` |
| 4 | 🔴 КРИТИЧЕСКАЯ | Открытый редирект через параметр `next` | `apps/accounts/views.py` |
| 5 | 🔴 КРИТИЧЕСКАЯ | Статус оплаты изменяется через неаутентифицированный GET | `apps/orders/views.py` |
| 6 | 🟠 ВЫСОКАЯ | Нет ограничения частоты запросов на вход/регистрацию | `apps/accounts/views.py` |
| 7 | 🟠 ВЫСОКАЯ | Перечисление имён пользователей/email через ошибки регистрации | `apps/accounts/views.py` |
| 8 | 🟠 ВЫСОКАЯ | `CartRemoveView` использует метод DELETE (граничный случай CSRF) | `apps/cart/views.py` |
| 9 | 🟠 ВЫСОКАЯ | Фиксация сессии — корзина теряется после входа | `apps/cart/cart.py` |
| 10 | 🟠 ВЫСОКАЯ | Нет максимального лимита количества товаров в корзине | `apps/cart/cart.py` |
| 11 | 🟠 ВЫСОКАЯ | Сессия вишлиста не ограничена — вектор DoS | `apps/cart/wishlist.py` |
| 12 | 🟠 ВЫСОКАЯ | `SESSION_COOKIE_HTTPONLY` явно не задан | `config/settings/base.py` |
| 13 | 🟡 СРЕДНЯЯ | `CSRF_COOKIE_HTTPONLY` явно не задокументирован | `config/settings/base.py` |
| 14 | 🟡 СРЕДНЯЯ | Нет `@login_required` в `AccountView` | `apps/accounts/views.py` |
| 15 | 🟡 СРЕДНЯЯ | Лимит загрузки 20 МБ на всех эндпоинтах | `config/settings/base.py` |
| 16 | 🟡 СРЕДНЯЯ | Поле телефона без валидации | `apps/orders/forms.py` |
| 17 | 🟡 СРЕДНЯЯ | Итоговая сумма заказа не проверяется на > 0 | `apps/orders/views.py` |
| 18 | 🟡 СРЕДНЯЯ | Image bomb — `MAX_IMAGE_PIXELS` не задан | `apps/catalog/models.py` |
| 19 | 🟡 СРЕДНЯЯ | Админка по стандартному URL `/admin/`, нет 2FA | `config/urls.py` |
| 20 | 🟡 СРЕДНЯЯ | `ALLOWED_HOSTS` может быть пустой строкой в продакшене | `config/settings/production.py` |
| 21 | 🟢 НИЗКАЯ | Куки сессии живут 30 дней | `config/settings/base.py` |
| 22 | 🟢 НИЗКАЯ | Нет заголовка `Content-Security-Policy` | `config/settings/production.py` |
| 23 | 🟢 НИЗКАЯ | `x-html` рендерит HTML сервера через `innerHTML` | `templates/partials/navbar.html` |
| 24 | 🟢 НИЗКАЯ | Нет `robots.txt` | — |
| 25 | 🟢 НИЗКАЯ | Устаревший `SECURE_BROWSER_XSS_FILTER` | `config/settings/production.py` |
| 26 | 🟢 НИЗКАЯ | Отсутствует `favicon.ico` — шум 404 в логах | `config/urls.py` |

---

*Итого: 5 критических · 7 высоких · 8 средних · 6 низких = 26 уязвимостей*
