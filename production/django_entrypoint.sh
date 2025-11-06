#!/bin/bash
set -euo pipefail

# usage check
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <DJANGO_SUPERUSER_USERNAME> <DJANGO_SUPERUSER_PASSWORD>"
  exit 1
fi

DJANGO_SUPERUSER_USERNAME="$1"
DJANGO_SUPERUSER_PASSWORD="$2"
DJANGO_SUPERUSER_EMAIL="admin@sample.com"

# export so subprocesses can read them
export DJANGO_SUPERUSER_USERNAME
export DJANGO_SUPERUSER_PASSWORD
export DJANGO_SUPERUSER_EMAIL

# 작업 디렉터리 (필요에 맞게 수정)
PROJECT_HOME="/home/ubuntu/KAIA_CSMS_BETA/KAIA_CSMS_BETA/kaia_app"
VENV_DIR="/home/ubuntu/myvenv"

# venv 생성(이미 있으면 덮어쓸 수도 있으므로, 원하면 존재 확인 로직 추가)
python3 -m venv "$VENV_DIR"
# activate
source "$VENV_DIR/bin/activate"

# 이동
cd "$PROJECT_HOME"

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

# 마이그레이션 (대화형 금지)
python manage.py migrate --noinput

# 슈퍼유저 생성 (create_superuser.py가 env 읽도록 작성되어 있어야 함)
# 예: create_superuser.py 내부에서 os.getenv("DJANGO_SUPERUSER_USERNAME") 등 사용
python manage.py shell < create_superuser.py

# static 수집 (대화형 금지)
python manage.py collectstatic --noinput

# 개발용 서버 실행 (테스트/개발 전용)
# 운영환경이라면 gunicorn/nginx 같은 구성 사용 권장
python manage.py runserver 0.0.0.0:8080
