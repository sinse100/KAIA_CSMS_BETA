@echo off
REM ========================================
REM  setup_and_run.bat
REM  Django 서버 세팅 및 실행 (사용자명 + 비밀번호 인자 입력)
REM  사용법:
REM    setup_and_run.bat admin mypassword123
REM ========================================

REM === 인자 확인 ===
IF "%~1"=="" (
    echo [!] 관리자 사용자명을 입력해야 합니다.
    echo 사용법: setup_and_run.bat USERNAME PASSWORD
    exit /b 1
)
IF "%~2"=="" (
    echo [!] 관리자 비밀번호를 입력해야 합니다.
    echo 사용법: setup_and_run.bat USERNAME PASSWORD
    exit /b 1
)

REM === 인자 할당 ===
set "DJANGO_SUPERUSER_USERNAME=%~1"
set "DJANGO_SUPERUSER_PASSWORD=%~2"
set "DJANGO_SUPERUSER_EMAIL=%~1@example.com"

REM === 가상환경 생성 및 활성화 ===
if not exist ..\myvenv (
    python -m venv ..\myvenv
)
call ..\myvenv\Scripts\activate.bat

REM ===python manage.py runserver할때마다 생성되는 캐시파일인 __pycache__ 생성 안되도록 설정====
set PYTHONDONTWRITEBYTECODE=1 
timeout /t 1 >nul

REM === 경로 변경 ===
cd /d ..\kaia_app

REM === pip 버전 최신화 ===
python.exe -m pip install --upgrade pip

REM === 패키지 설치 ===
pip install -r requirements.txt

REM === DB 마이그레이션 ===
python manage.py migrate --run-syncdb

REM === 관리자 계정 생성 ===
python manage.py createsuperuser --username %DJANGO_SUPERUSER_USERNAME% --email %DJANGO_SUPERUSER_EMAIL% --noinput || echo [!] 관리자 계정 이미 존재함

REM === 정적 파일 수집 ===
python manage.py collectstatic --noinput