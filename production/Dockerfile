# 1. 베이스 이미지 선택 (Debian/Ubuntu 계열)
FROM ubuntu:25.10

# 1. 기본 쉘을 bash로 설정
SHELL ["/bin/bash", "-c"]

# 2. 작업 디렉토리를 ubuntu로 설정
WORKDIR /home/ubuntu

# 3. gh CLI 설치에 필요한 패키지 및 ssh 설치
RUN apt-get update && apt-get install -y curl gpg ssh openssh-client git dos2unix

# 4. GitHub CLI 설치
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y gh

# 5. Docker 빌드 시 PAT를 인자로 받기 위한 설정
ARG GITHUB_TOKEN
ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG SECRET_KEY
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION
ARG AWS_STORAGE_BUCKET_NAME
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ARG GITHUB_REPO_NAME
ARG GITHUB_USERNAME

ENV EMAIL_HOST_USER=${EMAIL_HOST_USER}
ENV EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
ENV SECRET_KEY=${SECRET_KEY}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_REGION=${AWS_REGION}
ENV AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
ENV GITHUB_REPO_NAME=${GITHUB_REPO_NAME}
ENV GITHUB_USERNAME=${GITHUB_USERNAME}

# 6. 깃허브에 접근하기 위한 인증서 발급
RUN ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""
RUN echo "--- Generated Public Key ---"
RUN cat /root/.ssh/id_ed25519.pub
RUN echo "--------------------------"
RUN echo "Registering public key to GitHub..."
RUN export GH_TOKEN=${GITHUB_TOKEN} && gh ssh-key add /root/.ssh/id_ed25519.pub --title "My-Docker-SSH-Key"

RUN echo "SSH key has been generated and registered to GitHub."

RUN mkdir -p ~/.ssh && \
    chmod 700 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts

# 7. 깃허브 상의 krcsms 프로젝트 다운로드후 python 가상환경 생성
RUN git clone git@github.com:${GITHUB_USERNAME}/${GITHUB_REPO_NAME}.git
RUN apt-get update && \
    apt-get install git python3-pip python3-venv -y

# 8. 8080 번 포트 open
EXPOSE 8080

RUN chmod +x /home/ubuntu/${GITHUB_REPO_NAME}/django_entrypoint.sh

ENTRYPOINT /home/ubuntu/${GITHUB_REPO_NAME}/django_entrypoint.sh ${DJANGO_SUPERUSER_USERNAME} ${DJANGO_SUPERUSER_PASSWORD}
