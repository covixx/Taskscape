@echo off
python3 -m PyInstaller --onefile screensaver.py
move dist\screensaver.exe screensaver.scr
move screensaver.scr C:\Windows\System32