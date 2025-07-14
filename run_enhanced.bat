@echo off
echo VET-Assistant2 強化版投稿生成ツール起動中...
cd /d "%~dp0"
python -c "import sys; print('Python version:', sys.version)"
python -c "import tkinter; print('tkinter OK')"
python -c "import sqlite3; print('sqlite3 OK')"
echo.
echo 依存関係チェック完了。アプリを起動中...
python enhanced_post_generator.py
pause