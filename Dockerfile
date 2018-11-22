FROM alpine:3.7

MAINTAINER Mike Jewell 

RUN apk update

# Install base and dev packages
RUN apk add --no-cache --virtual .build-deps
RUN apk add bash

# Install build packages
RUN apk add make && apk add curl && apk add openssh

# Install git
RUN apk add git

# Set timezone to UTC by default
RUN ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime

RUN apk -Uuv add groff less python3

# Install aws-cli and docker-compose
RUN pip3 install awscli docker-compose==1.22.0 boto3

# Install dependencies for sfs-update
RUN pip3 install requests pyyaml giturlparse

# Clean up pip
RUN apk --purge -v del py-pip
RUN rm /var/cache/apk/*

# Use unicode
RUN locale-gen C.UTF-8 || true
ENV LANG=C.UTF-8

# Install ecs-cli
RUN curl -o /usr/local/bin/ecs-cli https://s3.amazonaws.com/amazon-ecs-cli/ecs-cli-linux-amd64-latest
RUN chmod +x /usr/local/bin/ecs-cli

# Install Docker
RUN set -ex \
  && export DOCKER_VERSION=$(curl --silent --fail --retry 3 https://download.docker.com/linux/static/stable/x86_64/ | grep -o -e 'docker-[.0-9]*-ce\.tgz' | sort -r | head -n 1) \
  && DOCKER_URL="https://download.docker.com/linux/static/stable/x86_64/${DOCKER_VERSION}" \
  && echo Docker URL: $DOCKER_URL \
  && curl --silent --show-error --location --fail --retry 3 --output /tmp/docker.tgz "${DOCKER_URL}" \
  && ls -lha /tmp/docker.tgz \
  && tar -xz -C /tmp -f /tmp/docker.tgz \
  && mv /tmp/docker/* /usr/bin \
  && rm -rf /tmp/docker /tmp/docker.tgz \
  && which docker \
  && (docker version || true)


RUN apk add --no-cache sudo
RUN adduser -D deployer;                                               \
    chgrp -R deployer /usr/local;                                      \
    find /usr/local -type d | xargs chmod g+w;                        \
    echo "deployer ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/default; \
    chmod 0440 /etc/sudoers.d/default

ADD create_repo.sh /home/deployer/create_repo.sh
RUN chmod +x /home/deployer/create_repo.sh
ADD create_repo.py /home/deployer/create_repo.py
RUN chmod +x /home/deployer/create_repo.py
ADD deploy_image.sh /home/deployer/deploy_image.sh
RUN chmod +x /home/deployer/deploy_image.sh
ADD tag_and_push.sh /home/deployer/tag_and_push.sh
RUN chmod +x /home/deployer/tag_and_push.sh

# SFS updater
ADD sfs_update.sh /home/deployer/sfs_update.sh
RUN chmod +x /home/deployer/sfs_update.sh
ADD sfs_update.py /home/deployer/sfs_update.py
RUN chmod +x /home/deployer/sfs_update.py

USER deployer

CMD ["/bin/sh"]
