# Python 3.9 Compatibility Guide

## Проблема

Проект изначально разрабатывался с использованием синтаксиса Python 3.10+, который несовместим с Python 3.9, используемым на сервере RunPod.

## Основные проблемы совместимости

### 1. Subscripted Generics (list[], dict[], tuple[], set[])

**Проблема:**
```python
def get_items() -> list[str]:  # ❌ TypeError в Python 3.9
    return []
```

**Решение:**
```python
from __future__ import annotations

def get_items() -> list[str]:  # ✅ Работает в Python 3.9
    return []
```

### 2. Union Types (X | Y)

**Проблема:**
```python
def process(value: str | None) -> int | None:  # ❌ TypeError в Python 3.9
    return None
```

**Решение:**
```python
from __future__ import annotations

def process(value: str | None) -> int | None:  # ✅ Работает в Python 3.9
    return None
```

## Что было сделано

### 1. Автоматические скрипты исправления

Созданы скрипты для автоматического добавления `from __future__ import annotations`:

- **`scripts/fix_python39_compatibility.py`** - исправляет файлы с `list[]`, `dict[]` синтаксисом
- **`scripts/fix_union_syntax.py`** - исправляет файлы с `str | None` синтаксисом
- **`scripts/fix_all_python39.py`** - сканирует весь проект и исправляет все проблемы

### 2. Исправленные файлы (всего 19 файлов)

#### Core модули:
- `core/plugins/base_service.py`
- `core/plugins/core_api.py`
- `core/locales/__init__.py`
- `core/locales/en.py`
- `core/locales/ru.py`
- `core/platform/telegram/keyboards/main_menu.py`
- `core/platform/telegram/utils.py`
- `core/platform/telegram/setup.py`
- `core/platform/telegram/media_sender.py`
- `core/platform/telegram/middlewares.py`
- `core/platform/telegram/handlers/service.py`
- `core/platform/telegram/admin/broadcast.py`
- `core/platform/telegram/admin/stats.py`

#### Payment модули:
- `core/payments/service.py`
- `core/payments/providers/base.py`
- `core/payments/providers/cryptobot.py`
- `core/payments/providers/stars.py`
- `core/payments/providers/platega.py`

#### Service модули:
- `services/ai_avatar/service.py`
- `services/gpt_image/service.py`
- `services/kling/service.py`
- `services/nano_banano/service.py`
- `services/nano_banano/api/fal_client.py`
- `services/nano_banano/database/models.py`
- `services/sora/service.py`
- `services/veo/service.py`
- `services/flux2_flex/service.py`

### 3. Диагностические скрипты

- **`scripts/diagnose_ai_avatar.py`** - проверяет установку и загрузку AI Avatar сервиса
- **`scripts/test_nano_import.py`** - детальная диагностика импорта nano_banano для поиска ошибок
- **`scripts/fix_services_status.py`** - сбрасывает статус сервисов с `error` на `active` в БД

## Правила для будущей разработки

### ✅ ЧТО НУЖНО ДЕЛАТЬ

1. **Всегда добавляйте импорт в начало новых файлов:**
   ```python
   """
   Module docstring
   """
   from __future__ import annotations
   
   from typing import Optional
   # остальные импорты...
   ```

2. **Используйте современный синтаксис типов:**
   ```python
   from __future__ import annotations
   
   def process(items: list[str]) -> dict[str, int]:
       return {}
   
   def get_value(key: str) -> str | None:
       return None
   ```

3. **Тестируйте на Python 3.9 перед деплоем:**
   ```bash
   python scripts/test_nano_import.py
   python scripts/diagnose_ai_avatar.py
   ```

### ❌ ЧТО НЕ НУЖНО ДЕЛАТЬ

1. **НЕ используйте старый синтаксис Optional:**
   ```python
   # ❌ Устаревший синтаксис
   from typing import Optional
   def get_value() -> Optional[str]:
       return None
   
   # ✅ Современный синтаксис
   from __future__ import annotations
   def get_value() -> str | None:
       return None
   ```

2. **НЕ используйте typing.List, typing.Dict:**
   ```python
   # ❌ Устаревший синтаксис
   from typing import List, Dict
   def process() -> List[Dict[str, int]]:
       return []
   
   # ✅ Современный синтаксис
   from __future__ import annotations
   def process() -> list[dict[str, int]]:
       return []
   ```

3. **НЕ забывайте очищать Python кэш после изменений:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

## Процедура деплоя на RunPod

1. **Коммит и пуш изменений:**
   ```bash
   git add -A
   git commit -m "Your changes"
   git push
   ```

2. **На RunPod обновить код:**
   ```bash
   cd /workspace/fubotai
   git pull
   ```

3. **Очистить Python кэш:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

4. **Если сервисы не загружаются, сбросить статусы:**
   ```bash
   python scripts/fix_services_status.py
   ```

5. **Перезапустить бота:**
   ```bash
   supervisorctl restart fubotai
   ```

6. **Проверить загрузку сервисов:**
   ```bash
   python scripts/diagnose_ai_avatar.py
   ```

## Автоматическое исправление

Если добавили новый код без `from __future__ import annotations`:

```bash
# Локально
python scripts/fix_all_python39.py
git add -A
git commit -m "Fix Python 3.9 compatibility"
git push

# На RunPod
cd /workspace/fubotai
git pull
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
supervisorctl restart fubotai
```

## Проверка совместимости

Перед деплоем всегда запускайте тест:

```bash
python scripts/test_nano_import.py
```

Если тест проходит успешно (все 3 шага с ✅), код совместим с Python 3.9.

## Важные замечания

1. **Python кэш** - главная причина проблем после обновления кода. Всегда очищайте его.
2. **Статусы сервисов в БД** - если сервис упал с ошибкой, его статус меняется на `error` и он не загружается при перезапуске. Используйте `fix_services_status.py`.
3. **Импорт должен быть первым** - `from __future__ import annotations` должен идти сразу после docstring, до всех других импортов.

## Контакты и поддержка

При возникновении проблем с совместимостью:
1. Запустите `python scripts/test_nano_import.py` для диагностики
2. Проверьте traceback на наличие `TypeError: 'type' object is not subscriptable`
3. Запустите `python scripts/fix_all_python39.py` для автоматического исправления
4. Очистите кэш и перезапустите бота
