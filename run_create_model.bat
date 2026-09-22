@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" -m src.create_model.main
pause
