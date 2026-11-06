
FROM ubuntu:24.04

# Cài các công cụ cần thiết cho Lab Linux cơ bản.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        coreutils \
        passwd \
    && rm -rf /var/lib/apt/lists/*

# Tạo tài khoản không có quyền root.
RUN useradd \
    --create-home \
    --uid 10001 \
    --shell /bin/bash \
    lab

ENV HOME=/home/lab

WORKDIR /home/lab

# Các lệnh chạy dưới tài khoản lab.
USER 10001:10001

CMD ["/bin/bash", "--noprofile", "--norc"]
