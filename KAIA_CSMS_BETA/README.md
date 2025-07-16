## 서버 실행
+ runserver 전에 반드시, 아래의 과정을 거칠 것 (Windows 기준)
  + 1. python -m venv kaia_env (가상환경 생성)
  + 2. .\kaia_env\Scripts\Activate (가상환경 실행)
  + 3. cd .\kaia_app (프로젝트 폴더로 이동)
  + 4. pip install -r requirements.txt (필요 파이썬 패키지 설치) 
  + 5. python manage.py migrate --run-syncdb (데이터베이스 테이블 생성 관련)
  + 6. python manage.py createsuperuser (Django 최고 관리자 계정 생성)
  + 7. python manage.py collectstatic (Static File 전용 폴더 생성)
  + 8. python manage.py runserver (테스트 서버 실행)

+ 디자인 관련 참고 :  https://www.figma.com/design/a1D9cLwo8dYPhDqgdWMkwF/KAIA?m=auto&t=wTBBIGq68c7sgL3T-6
+ 특별히 보면 좋을거 같은 메모는 '## (메모)'로 시작하는 주석으로 달아놓음 - 참고하시면 좋을 듯

## 프로젝트 폴더 구성
+ read_S3 : S3 버킷으로부터 파일 정보 조회 (스토리지 저장 및 업로드 디버깅 용)
+ upload_S3 : S3 버킷에 파일 정보 업로드  (스토리지 저장 및 업로드 디버깅 용)
+ test_zip : 평가 제출물 예시 Zip 파일
+ kaia_app (프로젝트 루트)
  + eval_service (실제 기능 관리 폴더 - 마이크로서비스 관련 폴더)
  + kaiamain (프로젝트 메인 폴더 - 백엔드 주요 설정(예: 서버 설정, 프로젝트 폴더 구조 설정 등))
  + manage.py (프로젝트 관리 인터페이스 - 서버 실행 코드 등 포함)
  + secrets.json (서버 암호화 키 등과 같은 비밀 값 저장 파일)
