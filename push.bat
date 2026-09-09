@echo off
chcp 65001 >nul
title blog 커밋 + 푸시
cd /d "%~dp0"

set "MSG=%*"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0push.ps1" -m "%MSG%"
set RC=%ERRORLEVEL%

echo.
if "%RC%"=="0" (
  echo [완료] 정상 종료
) else (
  echo [실패] 종료 코드 %RC% - 위의 빨간 안내를 확인하세요.
)
echo.
pause
