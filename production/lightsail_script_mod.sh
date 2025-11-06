#!/bin/bash


# lightsail_script.sh : 생성된 krcsms 도커 이미지를 pull해서 krcsms 컨테이너 동작시킴. 배포 가장 마지막 단계에 실행시켜야함


# 1. 패키지 목록 업데이트 및 필수 패키지 설치
sudo apt-get update
sudo apt-get -y install ca-certificates curl

# 2. 도커 공식 GPG 키 추가 (최신 방식)
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 3. 도커 저장소 설정 (상호작용 없는 방식)
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. 새로 추가된 저장소를 포함하여 패키지 목록 다시 업데이트
sudo apt-get update

# 5. 도커 엔진, CLI, Containerd 설치 (자동 'yes' 입력)
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# (customize required - [REDACTED]) ***중요!!!!!!!!!!!!!!!!!!!!********* [REDACTED] 부분을 자신의 dockerhub 비밀번호로 채울것
echo [REDACTED] | sudo docker login -u sinse100 --password-stdin

# (customize required - sinse100/kaiaapp:0.0) krcsms 가 설치된 도커 이미지를 pull 한다음 실행시킴 (자신이 dockerhub에 올린 이미지 정보 [자신의 게정]/[이미지 이름]:버전 에 맞게 입력할 것)
sudo docker pull sinse100/kaiaapp:0.0
sudo docker run -d -p 80:8080 -t sinse100/kaiaapp:0.0
