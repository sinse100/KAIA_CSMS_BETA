# KRCSMS 웹 서비스


## 개발 (Development) 환경 구축
1. 본 저장소 pull
2. development 폴더로 이동
3. development 폴더에 secret.txt 파일 복붙
    + 배포할 때는 secret.txt 파일 제외하고 배포해야 함 (API 키 등 주요 정보 노출 가능)
4. Powershell에서 관리자 계정 및 DB 생성 등과 같이 Django 개발환경 초기화를 위한 스크립트(```dev_env_init.bat```) 실행 
    + 관리자 계정의 이름(예: admin)과 비밀번호(예: myStrongPassword!)를 파라미터로 전달
```
./dev_env_init.bat admin myStrongPassword!
```
5. Powershell에서 서버 가동을 위한 스크립트(dev_env_runserver.bat) 실행 (python manage.py runserver 대용) 
```
./dev_env_runserver.bat
```

## 배포 (Work-In-Progess)
1. development 폴더에 secret.txt 삭제
2. 본 프로젝트 Git 저장소로 push
3. production 폴더로 이동
4. production 폴더에 secret.txt 파일 복붙
5. ....


## Resource
+ notion 서비스 요약 : https://www.notion.so/krcsms-26a1dd08e515802fa86df185619a5e19?source=copy_link
+ krcsms 사이트 :  http://www.krcsms.com
+ krcsms 디자인 :  https://www.figma.com/design/a1D9cLwo8dYPhDqgdWMkwF/KAIA?m=auto&t=QsdYQiQpu8OcwvYC-6
+ krcsms Dockerhub : https://hub.docker.com/repository/docker/sinse100/kaiaapp/general
