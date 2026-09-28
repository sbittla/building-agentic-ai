@echo off
REM Building Agentic AI Systems: run every chapter's exercises and keep their output.
REM Double-click this file, or run it with arguments that go to run-chapter:
REM     run-chapters.cmd                    every chapter, free local model (qwen3.5:9b)
REM     run-chapters.cmd 7                  just chapter 7
REM     run-chapters.cmd 7 --model claude   chapter 7 with Claude (needs your API key in .env)
REM     run-chapters.cmd all --free-only    only the exercises that need no model
REM The logs go to solutions\outputs (open solutions\outputs\README.md).
setlocal
cd /d "%~dp0"
set "FIRST=%~1"
set "ARGS=%*"
if "%FIRST%"=="" set "ARGS=all"
if "%FIRST%"=="" goto start
if "%FIRST:~0,1%"=="-" set "ARGS=all %*"
:start

REM The local model must be running (it downloads about 6.6 GB the first time), unless
REM you chose Claude or only the free exercises.
set "NEED_LOCAL=1"
if /i "%RUN_MODEL%"=="claude" set "NEED_LOCAL="
echo %ARGS% | findstr /i /c:"--model claude" /c:"--model=claude" /c:"--free-only" >nul
if not errorlevel 1 set "NEED_LOCAL="
if defined NEED_LOCAL (
    echo Starting the free local model first: course.cmd local up
    call "%~dp0course.cmd" local up
)

call "%~dp0course.cmd" run-chapter %ARGS% --yes
echo.
echo Finished. The output of every exercise is in the solutions\outputs folder;
echo open solutions\outputs\README.md for the overview.
pause
