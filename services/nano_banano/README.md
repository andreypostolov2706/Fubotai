# 🍌 Nano Banano — Сервис генерации изображений

## Описание

**Nano Banano** — сервис генерации и редактирования изображений с помощью ИИ (Google Gemini через fal.ai).

### Возможности:
- ✨ **Text-to-Image** — создание изображений по текстовому описанию
- 🖼 **Image-to-Image** — редактирование и объединение фотографий (до 4 шт.)
- 🚫 **Негативный промпт** — указание того, чего НЕ должно быть на изображении
- 📤 **Публикация в галерею** — возможность поделиться результатом в канале

### Две версии модели:
| Версия | Описание | Особенности |
|--------|----------|-------------|
| **Nano Banana** | Gemini 2.5 Flash Image | Быстрая, базовое качество |
| **Nano Banana Pro** | Gemini 3 Pro Image | Лучшее качество, разрешение до 4K |

---

## Структура файлов

```
services/nano_banano/
├── __init__.py              # Экспорт сервиса
├── service.py               # Главный класс NanoBananoService
├── config.py                # Константы, цены fal.ai
├── README.md                # Эта документация
│
├── api/
│   ├── __init__.py
│   └── fal_client.py        # Клиент fal.ai API
│
├── database/
│   ├── __init__.py
│   ├── connection.py        # SQLite подключение
│   └── models.py            # Модель Generation
│
├── handlers/
│   ├── __init__.py
│   ├── generate.py          # Text-to-Image логика
│   ├── edit.py              # Image-to-Image логика
│   ├── history.py           # История генераций
│   └── settings.py          # Настройки пользователя
│
├── keyboards.py             # Inline клавиатуры
├── messages.py              # Тексты сообщений
│
├── data/                    # Создаётся автоматически
│   └── nano_banano.db       # SQLite база данных
│
└── requirements.txt         # Зависимости (fal)
```

---

## API Endpoints (fal.ai)

| Режим | Обычная версия | Pro версия |
|-------|----------------|------------|
| **Text-to-Image** | `fal-ai/nano-banana` | `fal-ai/nano-banana-pro` |
| **Image-to-Image** | `fal-ai/nano-banana/edit` | `fal-ai/nano-banana-pro/edit` |

### Параметры API:

| Параметр | Тип | Значения | По умолчанию |
|----------|-----|----------|--------------|
| `prompt` | string | Текст промпта | — |
| `negative_prompt` | string | Что НЕ генерировать | — |
| `num_images` | int | 1-4 | 1 |
| `aspect_ratio` | enum | 1:1, 16:9, 9:16, 4:3, 3:4, и др. | 1:1 |
| `output_format` | enum | png, jpeg, webp | png |
| `image_urls` | list | URL изображений (для edit) | — |

### Только для Pro версии:

| Параметр | Тип | Значения | По умолчанию |
|----------|-----|----------|--------------|
| `resolution` | enum | 1K, 2K, 4K | 1K |
| `enable_web_search` | bool | Поиск в интернете | false |

---

## Расчёт стоимости

### Формула:

```
Стоимость GTON = (Цена fal.ai в USD) × (1 + Маржа) × (Курс USD→GTON)
```

### Базовые цены fal.ai:

| Модель | Разрешение | Цена USD |
|--------|------------|----------|
| Nano Banana | — | $0.04 |
| Nano Banana Pro | 1K | $0.15 |
| Nano Banana Pro | 2K | $0.22 |
| Nano Banana Pro | 4K | $0.30 |

### Пример расчёта:

```
Исходные данные:
- Цена fal.ai: $0.15 (nano-banana-pro 1K)
- Маржа: 30% (настройка админа)
- Курс: 1 GTON = $10 (из ядра)

Расчёт:
1. Себестоимость:     $0.15
2. С маржой 30%:      $0.15 × 1.30 = $0.195
3. Конвертация:       $0.195 ÷ $10 = 0.0195 GTON
4. Округление (4 знака): 0.0195 GTON

Итого: 0.0195 GTON
```

### Проверка баланса:

Перед генерацией проверяем, что баланс пользователя >= стоимости с маржой.

---

## Настройки сервиса (Админ)

```python
service_config = {
    # API ключ fal.ai
    "fal_api_key": "",
    
    # Маржа (множитель, 0.3 = +30%)
    "margin_multiplier": 0.3,
    
    # Базовые цены fal.ai в USD
    "prices": {
        "nano_banana": 0.04,
        "nano_banana_pro_1k": 0.15,
        "nano_banana_pro_2k": 0.22,
        "nano_banana_pro_4k": 0.30,
    },
    
    # Реферальный бонус
    "referral_bonus_enabled": True,
    "referral_bonus_percent": 10,
    
    # Галерея (канал для публикаций)
    "gallery_channel_id": "",      # @channel или -100123456
    "gallery_enabled": False,
    
    # Лимиты
    "max_images_per_request": 4,   # Макс. изображений за раз
    "max_input_images": 4,         # Макс. входных фото для edit
}
```

---

## Настройки пользователя

```python
user_settings = {
    # Версия модели
    "model": "nano_banana",        # nano_banana | nano_banana_pro
    
    # Размер изображения
    "aspect_ratio": "1:1",         # 1:1, 16:9, 9:16, 4:3, 3:4
    
    # Формат выходного файла
    "output_format": "png",        # png, jpeg, webp
    
    # Разрешение (только для Pro)
    "resolution": "1K",            # 1K, 2K, 4K
}
```

---

## FSM состояния

| Состояние | Описание | Данные |
|-----------|----------|--------|
| `waiting_prompt` | Ожидание промпта | `mode`: "generate" или "edit" |
| `waiting_negative` | Ожидание негативного промпта | `prompt`, `mode` |
| `waiting_images` | Ожидание фотографий (edit) | `images`: [] |
| `waiting_edit_prompt` | Ожидание промпта для edit | `images` |
| `confirming` | Подтверждение генерации | `prompt`, `negative`, `images`, `cost` |
| `generating` | Процесс генерации | `request_id`, `start_time` |

---

## Пользовательский флоу

### Главное меню

```
🍌 Nano Banano

💰 Баланс: 15.5000 GTON

Выберите действие:

[✨ Создать изображение]
[🖼 Редактировать фото]
[📂 Мои генерации]
[⚙️ Настройки]
[◀️ Главное меню]
```

---

### Флоу 1: Text-to-Image

```
1. [✨ Создать изображение]
        ↓
2. "Введите описание изображения:"
   [FSM: waiting_prompt, mode=generate]
        ↓
3. Пользователь вводит промпт
        ↓
4. "Что НЕ должно быть на изображении? (необязательно)"
   [⏭ Пропустить] [❌ Отмена]
   [FSM: waiting_negative]
        ↓
5. Пользователь вводит негатив или пропускает
        ↓
6. Экран подтверждения:
   ┌─────────────────────────────────────┐
   │ 📋 Подтверждение                    │
   │                                      │
   │ 📝 Промпт: "..."                     │
   │ 🚫 Негатив: "..."                    │
   │                                      │
   │ 🤖 Модель: Nano Banana Pro           │
   │ 📐 Размер: 1:1                       │
   │ 📊 Разрешение: 1K                    │
   │                                      │
   │ 💰 Стоимость: ~0.0195 GTON           │
   │                                      │
   │ [✅ Создать] [✏️ Изменить] [❌ Отмена]│
   └─────────────────────────────────────┘
        ↓
7. [✅ Создать] → Списание GTON → Генерация
        ↓
8. Анимированный прогресс:
   "⏳ Генерация... 🍌🍌🍌⬜⬜⬜⬜ 30%"
        ↓
9. Результат:
   [ФОТО]
   ┌─────────────────────────────────────┐
   │ ✅ Готово!                           │
   │ 💰 Списано: 0.0195 GTON              │
   │ ⏱ Время: 12.3 сек                    │
   │                                      │
   │ [🔄 Ещё раз] [📤 В галерею] [◀️ Меню]│
   └─────────────────────────────────────┘
```

---

### Флоу 2: Image-to-Image

```
1. [🖼 Редактировать фото]
        ↓
2. "Отправьте от 1 до 4 фотографий:"
   [FSM: waiting_images]
        ↓
3. Пользователь отправляет фото (1-4 шт.)
   "📷 Получено: 2 фото"
   [📷 Добавить ещё] [✅ Готово]
        ↓
4. [✅ Готово]
        ↓
5. "Опишите, что сделать с фото:"
   [FSM: waiting_edit_prompt]
        ↓
6. Пользователь вводит промпт
        ↓
7. (Далее как в Text-to-Image: негатив → подтверждение → генерация)
```

---

### Кнопка "✏️ Изменить"

При нажатии показывает меню:

```
✏️ Что изменить?

[📝 Промпт]
[🚫 Негативный промпт]
[🤖 Модель]
[📐 Размер]
[📊 Разрешение]
[◀️ Назад к подтверждению]
```

---

### Меню настроек

```
⚙️ Настройки Nano Banano

🤖 Модель:
   [Nano Banana] [Nano Banana Pro ✓]

📐 Размер изображения:
   [1:1 ✓] [16:9] [9:16] [4:3] [3:4]

🖼 Формат:
   [PNG ✓] [JPEG] [WebP]

📊 Разрешение (только Pro):
   [1K ✓] [2K] [4K]

[◀️ Назад]
```

---

### История генераций

```
📂 Мои генерации

Всего: 47 изображений

[Превью 1] [Превью 2] [Превью 3]
[Превью 4] [Превью 5] [Превью 6]

[◀️ 1/8 ▶️]
[◀️ Назад]
```

При нажатии на превью:

```
[ПОЛНОЕ ФОТО]

📝 Промпт: "Кот в космосе..."
🚫 Негатив: "текст, размытие"
🤖 Модель: Nano Banana Pro
📐 Размер: 1:1
💰 Стоимость: 0.0195 GTON
📅 Дата: 17.12.2024 22:15

[🔄 Повторить] [📤 В галерею] [🗑 Удалить] [◀️ Назад]
```

---

### Публикация в галерею

```
📤 Публикация в галерею

Ваше изображение будет опубликовано
в канале @nano_banano_gallery
вместе с промптом.

[✅ Опубликовать] [❌ Отмена]
```

Формат публикации в канале:

```
[ИЗОБРАЖЕНИЕ]

🍌 Nano Banano

📝 Промпт: "Кот в космосе, реалистичный стиль"
🤖 Модель: Nano Banana Pro

👤 Автор: @username
```

---

## Обработка ошибок

### Ошибка fal.ai:

```
1. Пользователь нажимает "✅ Создать"
2. Списываем GTON
3. Отправляем запрос в fal.ai
4. fal.ai возвращает ошибку
5. Возвращаем GTON пользователю:
   await self.core.add_balance(
       user_id=user_id,
       amount=cost,
       source="refund",
       reason="Возврат за неудачную генерацию Nano Banano"
   )
6. Показываем сообщение:
   "❌ Ошибка генерации. GTON возвращены на баланс."
```

### Недостаточно средств:

```
❌ Недостаточно GTON

Стоимость: 0.0195 GTON
Ваш баланс: 0.0100 GTON

[💳 Пополнить] [◀️ Назад]
```

---

## База данных

### Модель Generation

```python
class Generation(Base):
    """История генераций"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # Тип генерации
    mode = Column(String(20))              # "generate" | "edit"
    
    # Параметры
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    model = Column(String(50))             # nano_banana | nano_banana_pro
    aspect_ratio = Column(String(10))      # 1:1, 16:9, etc.
    resolution = Column(String(5))         # 1K, 2K, 4K
    output_format = Column(String(10))     # png, jpeg, webp
    
    # Входные изображения (для edit)
    input_images = Column(JSON)            # ["url1", "url2"]
    
    # Результат
    image_url = Column(String(500))
    file_id = Column(String(100))          # Telegram file_id
    
    # Стоимость
    cost_usd = Column(Numeric(10, 4))      # Себестоимость fal.ai
    cost_gton = Column(Numeric(18, 6))     # Списано с пользователя
    
    # Метаданные
    generation_time = Column(Float)        # Время генерации (сек)
    fal_request_id = Column(String(100))
    
    # Статус
    status = Column(String(20))            # pending, completed, failed, refunded
    error_message = Column(Text)
    
    # Публикация
    published_to_gallery = Column(Boolean, default=False)
    published_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
```

---

## Анимированный прогресс

```python
PROGRESS_FRAMES = [
    "🍌⬜⬜⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌⬜⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌⬜⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌⬜⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌⬜⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌⬜⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌⬜⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌⬜⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌🍌⬜",
    "🍌🍌🍌🍌🍌🍌🍌🍌🍌🍌",
]

async def animate_progress(message, start_time, estimated_time=15):
    """Анимация прогресса генерации"""
    while True:
        elapsed = time.time() - start_time
        progress = min(elapsed / estimated_time, 0.95)  # Макс 95% до завершения
        frame_idx = int(progress * len(PROGRESS_FRAMES))
        frame = PROGRESS_FRAMES[min(frame_idx, len(PROGRESS_FRAMES) - 1)]
        
        text = f"⏳ Генерация...\n\n{frame} {int(progress * 100)}%"
        
        await message.edit_text(text)
        await asyncio.sleep(1)
```

---

## Callback формат

```
service:nano_banano:main              — Главное меню
service:nano_banano:generate          — Начать генерацию
service:nano_banano:edit              — Начать редактирование
service:nano_banano:history           — История
service:nano_banano:history:page:2    — Страница истории
service:nano_banano:history:view:123  — Просмотр генерации
service:nano_banano:settings          — Настройки
service:nano_banano:settings:model:pro — Выбор модели
service:nano_banano:settings:ratio:16:9 — Выбор размера
service:nano_banano:confirm           — Подтверждение
service:nano_banano:confirm:create    — Создать
service:nano_banano:confirm:edit      — Изменить параметры
service:nano_banano:confirm:cancel    — Отмена
service:nano_banano:skip_negative     — Пропустить негатив
service:nano_banano:gallery:publish   — Опубликовать в галерею
service:nano_banano:repeat:123        — Повторить генерацию
service:nano_banano:delete:123        — Удалить генерацию
```

---

## Зависимости

### requirements.txt

```
fal-client>=0.4.0
```

---

## Установка

1. Убедитесь, что FuBot установлен и работает
2. Получите API ключ на https://fal.ai
3. В админ-панели бота:
   - Перейдите в "Сервисы" → "Nano Banano" → "Настройки"
   - Укажите `fal_api_key`
   - Настройте маржу и другие параметры
4. Перезапустите бота

---

## Чеклист реализации

### Обязательно:
- [ ] `__init__.py` — экспорт NanoBananoService
- [ ] `service.py` — главный класс
- [ ] `config.py` — константы
- [ ] `api/fal_client.py` — клиент fal.ai
- [ ] `database/models.py` — модель Generation
- [ ] `database/connection.py` — подключение SQLite
- [ ] `handlers/generate.py` — Text-to-Image
- [ ] `handlers/edit.py` — Image-to-Image
- [ ] `handlers/history.py` — история генераций
- [ ] `handlers/settings.py` — настройки пользователя
- [ ] `keyboards.py` — все клавиатуры
- [ ] `messages.py` — тексты сообщений
- [ ] Анимированный прогресс
- [ ] Публикация в галерею
- [ ] Возврат GTON при ошибке

### Опционально (v2):
- [ ] Пакетная генерация (несколько изображений)
- [ ] Избранное
- [ ] Поиск по истории
- [ ] Статистика использования

---

*Документ создан: 17.12.2024*
