@echo off
setlocal

REM ===== 환경 파일 (배치와 같은 폴더의 secret.txt) =====
set "ENV_FILE=%~dp0secret.txt"

REM ===== PS1 호출: 캐럿(^) 없음, 한 줄 =====
for /f "usebackq delims=" %%L in (`
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0parse_env.ps1" -Path "%ENV_FILE%"
`) do (
  for /f "tokens=1,* delims==" %%A in ("%%L") do (
    set "%%A=%%B"
  )
)

REM ===python manage.py runserver할때마다 생성되는 캐시파일인 __pycache__ 생성 안되도록 설정====
set PYTHONDONTWRITEBYTECODE=1 
timeout /t 1 >nul

echo.
echo ====== [ENV LOADED] ======
echo EMAIL_HOST_USER=%EMAIL_HOST_USER%
echo EMAIL_HOST_PASSWORD=%EMAIL_HOST_PASSWORD%
echo SECRET_KEY=%SECRET_KEY%
echo AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
echo AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
echo AWS_REGION=%AWS_REGION%
echo AWS_STORAGE_BUCKET_NAME=%AWS_STORAGE_BUCKET_NAME%
echo ===========================
echo.

REM === 경로 변경 ===
cd /d ..\kaia_app

REM === django 서버 가동 ===
call ..\myvenv\Scripts\activate.bat
python manage.py runserver

endlocal & (
  set EMAIL_HOST_USER=%EMAIL_HOST_USER%
  set EMAIL_HOST_PASSWORD=%EMAIL_HOST_PASSWORD%
  set SECRET_KEY=%SECRET_KEY%
  set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID%
  set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY%
  set AWS_REGION=%AWS_REGION%
  set AWS_STORAGE_BUCKET_NAME=%AWS_STORAGE_BUCKET_NAME%
)

