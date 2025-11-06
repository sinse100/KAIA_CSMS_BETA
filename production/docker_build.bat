#!/bin/bash

# docker_build.sh : krcsms 도커 이미지 빌드 자동화 스크립트 (배포 첫번째 단계에서 실행시켜야함. 본 스크립트 실행 완료한 후에는 필요에 따라서 Dockerhub에 올리면됨)

EMAIL_HOST_USER=$1                ## 인증 번호 발송용 이메일
EMAIL_HOST_PASSWORD=$2            ## 인증 번호 발송용 이메일의 일회용 비밀번호
SECRET_KEY=$3                     ## Djagno에서 사용하는 비밀키
AWS_ACCESS_KEY_ID=$4              ## AWS API 키 (공개키)
AWS_SECRET_ACCESS_KEY=$5          ## AWS API 키 (개인키)
AWS_REGION=$6                     ## AWS 리전
AWS_STORAGE_BUCKET_NAME=$7        ## AWS S3 저장소 이름
GITHUB_TOKEN=$8                   ## github krcsms 저장소 접근을 위한 토큰
DJANGO_SUPERUSER_USERNAME=$9      ## Django 관리자 Username
DJANGO_SUPERUSER_PASSWORD=$10     ## Django 관리자 비밀번호
GITHUB_REPO_NAME=$11              ## krcsms 깃허브 저장소 이름
DOCKER_USERNAME=$12              ## krcsms 깃허브 저장소 이름

# 1. krcsms 서비스 동작을 위한 credential(예: AWS API 키)을 같이 넘겨줘서 이미지 빌드
docker build --no-cache \
--build-arg EMAIL_HOST_USER="$EMAIL_HOST_USER" \                   
--build-arg EMAIL_HOST_PASSWORD="$EMAIL_HOST_PASSWORD" \           
--build-arg SECRET_KEY="$SECRET_KEY" \                         
--build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \           
--build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \   
--build-arg AWS_REGION="$AWS_REGION" \                        
--build-arg AWS_STORAGE_BUCKET_NAME="$AWS_STORAGE_BUCKET_NAME" \      
--build-arg GITHUB_TOKEN="$GITHUB_TOKEN" \  
--build-arg DJANGO_SUPERUSER_USERNAME="$DJANGO_SUPERUSER_USERNAME" \   
--build-arg DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" \      
--build-arf GITHUB_USERNAME="$GITHUB_USERNAME" \
--build-arg GITHUB_REPO_NAME="$GITHUB_REPO_NAME" \ -t kaiaapp:0.0 .       

# 2. 도커 이미지 제대로 동작하는지 확인
docker run -d -p 80:8080 -t $DOCKER_USERNAME/kaiaapp:0.0 "/bin/bash"
