@echo off
chcp 65001 > nul
title MovieHub Telegram Bot

echo =======================================================
echo         🎬 MovieHub Telegram Bot Ishga Tushirish
echo =======================================================
echo.

:: Python tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python tizimda topilmadi!
    echo Iltimos, Python ni o'rnating va PATH ga qo'shing.
    pause
    exit /b
)

:: Kutubxonalarni tekshirish va o'rnatish
echo [1/2] Kutubxonalar tekshirilmoqda...
pip install -r requirements.txt --quiet

:: Botni ishga tushirish
echo [2/2] Bot ishga tushirilmoqda...
echo.
python main.py

echo.
echo Bot to'xtadi.
pause
