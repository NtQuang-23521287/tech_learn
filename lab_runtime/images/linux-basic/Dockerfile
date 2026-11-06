FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        coreutils \
        passwd \
        libnss-wrapper \
    && rm -rf /var/lib/apt/lists/*

# Tài khoản nền không có quyền root
RUN groupadd -g 10001 lab \
    && useradd -m -u 10001 -g 10001 \
        -s /bin/bash lab

# Script khởi tạo tên học viên
COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

USER 10001:10001

WORKDIR /

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
