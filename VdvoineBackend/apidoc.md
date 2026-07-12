# API Documentation

**Base URL:** `http://localhost:8000/api`  
**Format:** JSON  
**Auth:** сессионная аутентификация через cookie (устанавливается автоматически при первом запросе к корзине)

> Все запросы из Next.js должны отправляться с `credentials: 'include'` чтобы передавать session cookie.

---

## Общие принципы

### Сессия пользователя
API не требует регистрации. При первом обращении к `/api/basket/` Django создаёт сессию и устанавливает cookie `sessionid`. Все дальнейшие запросы привязаны к этой сессии — корзина, заказы.

### Коды ответов
| Код | Значение |
|-----|----------|
| `200` | Успех |
| `201` | Создан |
| `204` | Успех, тело пустое (DELETE) |
| `400` | Ошибка валидации |
| `404` | Не найдено |

### Формат ошибок
```json
{ "detail": "Текст ошибки" }
```
или при ошибках валидации полей:
```json
{ "field_name": ["Текст ошибки"] }
```

---

## 1. Products

### 1.1 Список товаров
```
GET /api/products/
```

**Query параметры:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `collection` | integer | Фильтр по ID коллекции |
| `size` | integer | Фильтр по ID размера (только товары в наличии) |
| `ordering` | string | Сортировка: `price`, `-price`, `name`, `-name` |

**Пример запроса:**
```
GET /api/products/?collection=1&ordering=-price
```

**Ответ `200`:**
```json
[
  {
    "id": 1,
    "name": "Футболка оверсайз",
    "image": "/media/products/tshirt.jpg",
    "price": "2500.00",
    "collection": {
      "id": 1,
      "name": "Лето 2025",
      "date": "2025-05-01",
      "is_active": true
    }
  }
]
```

---

### 1.2 Детальная страница товара
```
GET /api/products/<id>/
```

**Ответ `200`:**
```json
{
  "id": 1,
  "name": "Футболка оверсайз",
  "description": "Описание товара...",
  "image": "/media/products/tshirt.jpg",
  "price": "2500.00",
  "collection": {
    "id": 1,
    "name": "Лето 2025",
    "date": "2025-05-01",
    "is_active": true
  },
  "variants": [
    {
      "id": 3,
      "size": { "id": 1, "name": "S" },
      "quantity": 5
    },
    {
      "id": 4,
      "size": { "id": 2, "name": "M" },
      "quantity": 0
    }
  ]
}
```

> `quantity: 0` — размер недоступен, кнопку добавления в корзину нужно блокировать на фронте.

**Ответ `404`:**
```json
{ "detail": "Товар не найден." }
```

---

### 1.3 Список коллекций
```
GET /api/products/collections/
```

**Ответ `200`:**
```json
[
  {
    "id": 1,
    "name": "Лето 2025",
    "date": "2025-05-01",
    "is_active": true
  }
]
```
> Возвращает только активные коллекции (`is_active: true`).

---

### 1.4 Коллекция с товарами
```
GET /api/products/collections/<id>/
```

**Ответ `200`:**
```json
{
  "collection": {
    "id": 1,
    "name": "Лето 2025",
    "date": "2025-05-01",
    "is_active": true
  },
  "products": [
    {
      "id": 1,
      "name": "Футболка оверсайз",
      "image": "/media/products/tshirt.jpg",
      "price": "2500.00",
      "collection": { ... }
    }
  ]
}
```

---

## 2. Basket

> Все запросы к корзине требуют `credentials: 'include'`. Сессия создаётся автоматически.

### 2.1 Получить корзину
```
GET /api/basket/
```

**Ответ `200`:**
```json
[
  {
    "id": 7,
    "count": 2,
    "created_timestamp": "2025-07-01T14:30:00Z",
    "product": {
      "id": 3,
      "size": { "id": 1, "name": "S" },
      "quantity": 5,
      "product_card": {
        "id": 1,
        "name": "Футболка оверсайз",
        "image": "/media/products/tshirt.jpg",
        "price": "2500.00",
        "collection": { ... }
      }
    }
  }
]
```

---

### 2.2 Добавить товар в корзину
```
POST /api/basket/
```

**Тело запроса:**
```json
{
  "product_id": 3,
  "count": 2
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `product_id` | integer | ✅ | ID варианта товара (`ProductVariant.id`) |
| `count` | integer | ✅ | Количество (> 0) |

> Если товар уже в корзине — количество обновится, новая запись не создастся.

**Ответ `201`:** — объект корзины (см. формат выше)

**Ответ `400`:**
```json
{ "count": ["Недостаточно товара на складе. Доступно: 3"] }
```

---

### 2.3 Обновить количество позиции
```
PATCH /api/basket/<id>/
```

**Тело запроса:**
```json
{ "count": 3 }
```

**Ответ `200`:** — обновлённый объект корзины

**Ответ `404`:**
```json
{ "detail": "Позиция не найдена." }
```

---

### 2.4 Удалить позицию из корзины
```
DELETE /api/basket/<id>/
```

**Ответ `204`:** — пустое тело

---

### 2.5 Очистить корзину
```
DELETE /api/basket/clear/
```

**Ответ `204`:** — пустое тело

---

## 3. Orders

### 3.1 Список заказов сессии
```
GET /api/orders/
```

**Ответ `200`:**
```json
[
  {
    "id": 12,
    "full_name": "Иван Иванов",
    "status": "pending",
    "payment_status": "waiting",
    "total_price": "4750.00",
    "created_timestamp": "2025-07-01T15:00:00Z"
  }
]
```

**Статусы заказа (`status`):**
| Значение | Описание |
|----------|----------|
| `pending` | Ожидает подтверждения |
| `confirmed` | Подтверждён |
| `paid` | Оплачен |
| `shipped` | Отправлен |
| `delivered` | Доставлен |
| `cancelled` | Отменён |

**Статусы оплаты (`payment_status`):**
| Значение | Описание |
|----------|----------|
| `waiting` | Ожидает оплаты |
| `paid` | Оплачен |
| `failed` | Ошибка оплаты |
| `refunded` | Возврат |

---

### 3.2 Создать заказ
```
POST /api/orders/
```

> Товары берутся из корзины текущей сессии автоматически. После создания заказа корзина очищается, остатки на складе списываются.

**Тело запроса:**
```json
{
  "full_name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "city": "Москва",
  "pickup_point": "ПВЗ на ул. Ленина, 5",
  "promo_code": "SUMMER20"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `full_name` | string | ✅ | ФИО получателя |
| `email` | string | ✅ | Email |
| `phone` | string | ✅ | Телефон |
| `city` | string | ✅ | Город |
| `pickup_point` | string | ❌ | Пункт выдачи |
| `promo_code` | string | ❌ | Код промокода (скидка в % от суммы) |

**Ответ `201`:** — полный объект заказа (см. 3.3)

**Ответ `400`:**
```json
{ "non_field_errors": ["Корзина пуста"] }
```
```json
{ "promo_code": ["Промокод не найден"] }
```
```json
{ "non_field_errors": ["Недостаточно товара «Футболка оверсайз» на складе"] }
```

---

### 3.3 Детали заказа
```
GET /api/orders/<id>/
```

**Ответ `200`:**
```json
{
  "id": 12,
  "full_name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "city": "Москва",
  "pickup_point": "ПВЗ на ул. Ленина, 5",
  "promo_code": "SUMMER20",
  "total_price": "4750.00",
  "status": "pending",
  "payment_status": "waiting",
  "created_timestamp": "2025-07-01T15:00:00Z",
  "items": [
    {
      "id": 1,
      "count": 2,
      "price": "2500.00",
      "total": "5000.00",
      "product": {
        "id": 3,
        "size": { "id": 1, "name": "S" },
        "quantity": 3,
        "product_card": {
          "id": 1,
          "name": "Футболка оверсайз",
          "image": "/media/products/tshirt.jpg",
          "price": "2500.00",
          "collection": { ... }
        }
      }
    }
  ]
}
```

---

### 3.4 Отменить заказ
```
PATCH /api/orders/<id>/cancel/
```

> Отмена доступна только при статусе `pending` или `confirmed`.

**Ответ `200`:** — обновлённый объект заказа со статусом `cancelled`

**Ответ `400`:**
```json
{ "detail": "Нельзя отменить заказ со статусом «Отправлен»." }
```

---

## 4. Promotions

### 4.1 Проверить промокод
```
POST /api/promotions/validate/
```

> Вызывать при вводе кода пользователем на странице оформления заказа — до сабмита формы.

**Тело запроса:**
```json
{ "code": "SUMMER20" }
```

**Ответ `200` (промокод валиден):**
```json
{
  "valid": true,
  "promo": {
    "id": 1,
    "code": "SUMMER20",
    "discount_value": 20,
    "is_active": true
  }
}
```
> `discount_value` — процент скидки. Итоговая сумма считается на бэкенде при создании заказа.

**Ответ `400` (промокод не найден или исчерпан):**
```json
{
  "valid": false,
  "errors": {
    "code": ["Промокод не найден."]
  }
}
```

---

## Типичные сценарии

### Покупка товара (happy path)
```
1. GET  /api/products/              — загрузить каталог
2. GET  /api/products/<id>/         — открыть карточку товара
3. POST /api/basket/                — добавить вариант в корзину
4. GET  /api/basket/                — показать корзину
5. POST /api/promotions/validate/   — (опционально) проверить промокод
6. POST /api/orders/                — оформить заказ
7. GET  /api/orders/<id>/           — показать страницу "Заказ принят"
```

### Управление корзиной
```
PATCH  /api/basket/<id>/   { "count": 3 }  — изменить количество
DELETE /api/basket/<id>/                   — удалить позицию
DELETE /api/basket/clear/                  — очистить всё
```

---

## Настройка fetch в Next.js

```js
// lib/api.js
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    credentials: 'include',           // обязательно для сессии
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw { status: res.status, data: error }
  }

  if (res.status === 204) return null
  return res.json()
}

// Примеры использования:
// apiFetch('/products/')
// apiFetch('/basket/', { method: 'POST', body: JSON.stringify({ product_id: 3, count: 1 }) })
// apiFetch(`/orders/${id}/cancel/`, { method: 'PATCH' })
```

> **CORS:** в Django нужно установить `django-cors-headers` и добавить в `CORS_ALLOWED_ORIGINS` адрес Next.js (`http://localhost:3000`). Также установить `CORS_ALLOW_CREDENTIALS = True`.