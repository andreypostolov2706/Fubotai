#!/bin/bash
echo "=== Checking code version ==="
echo "Git commit:"
git log -1 --oneline
echo ""
echo "Checking router.py for logging:"
grep -n "logger.info.*Callback router received" core/platform/telegram/router.py || echo "NOT FOUND"
echo ""
echo "Checking main_menu.py for logging:"
grep -n "logger.info.*Service.*menu items" core/platform/telegram/keyboards/main_menu.py || echo "NOT FOUND"
