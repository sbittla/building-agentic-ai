@echo off
REM Batch file to run the PowerShell symlink creation script
REM This script must be run from the building-agentic-ai directory

cd /d "%~dp0"

echo Running PowerShell script to create symlinks...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "generate_symlinks.ps1" -Force

echo.
echo Script execution complete. Check the output above for results.
pause
