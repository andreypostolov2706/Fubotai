# Quick Start Guide - Быстрый старт

## Новый файл Python

При создании нового `.py` файла **ВСЕГДА** начинайте с:

```python
"""
Module description
"""
from __future__ import annotations

from typing import Optional
# остальные импорты...
```

## Деплой на RunPod - 5 команд

```bash
# 1. Обновить код
cd /workspace/fubotai && git pull

# 2. Очистить кэш
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null && find . -name "*.pyc" -delete

# 3. Сбросить статусы сервисов (если нужно)
python scripts/fix_services_status.py

# 4. Перезапустить бота
supervisorctl restart fubotai

# 5. Проверить загрузку
python scripts/diagnose_ai_avatar.py
```

## Если что-то сломалось

```bash
# Автоматически исправить все проблемы Python 3.9
python scripts/fix_all_python39.py

# Очистить кэш
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Перезапустить
supervisorctl restart fubotai
```

## Проверка перед коммитом

```bash
# Тест импорта
python scripts/test_nano_import.py

# Если ✅ на всех 3 шагах - всё ок!
```

## Главное правило

**ВСЕГДА добавляйте `from __future__ import annotations` в начало файла!**

Это решает все проблемы с типами в Python 3.9.

---

Подробности: [PYTHON39_COMPATIBILITY.md](./PYTHON39_COMPATIBILITY.md)
