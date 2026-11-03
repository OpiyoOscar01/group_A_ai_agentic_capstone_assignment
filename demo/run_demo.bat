@echo off
cd /d "%~dp0.."
python src\web_ui.py %*
if errorlevel 1 pause
