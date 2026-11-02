# TechLearn — Ghi chú 01: Git, môi trường ảo và `manage.py` trong Django

> **Dự án:** TechLearn — nền tảng học Linux, Network và thực hành lab trực tuyến  
> **Môi trường:** Ubuntu (WSL), Python virtual environment `.techlearn`  

## 1. Cấu trúc repository hiện tại

Thư mục `~/tech_learn` chứa mã nguồn nói chung; repository Git đã clone nằm tại:

```text
/home/quangnt/tech_learn/
└── tech_learn/                 # Git repository (project root)
    ├── .git/
    ├── .gitignore
    ├── .techlearn/             # Python virtual environment — KHÔNG commit
    ├── README.md
    ├── requirements.txt
    ├── manage.py
    └── doc/                    # Ghi chú học và tài liệu dự án
```

Mọi lệnh Git và Django trong ghi chú này được chạy tại **project root**:

```bash
cd ~/tech_learn/tech_learn
pwd
git rev-parse --show-toplevel
```

Kết quả đúng của hai lệnh kiểm tra đường dẫn là `/home/quangnt/tech_learn/tech_learn`.

## 2. Vì sao Django có `manage.py`?

Tên chính xác là **`manage.py`**, không phải `manager.py`.

Đây là file tiện ích dòng lệnh thường được Django tạo tự động khi dùng `django-admin startproject`. File này giúp chạy các tác vụ quản lý dự án:

| Lệnh | Ý nghĩa |
| --- | --- |
| `python manage.py --version` | In phiên bản Django |
| `python manage.py runserver` | Chạy development server (không dùng cho production) |
| `python manage.py migrate` | Áp dụng database migrations |
| `python manage.py createsuperuser` | Tạo tài khoản quản trị |
| `python manage.py test` | Chạy tests |
| `python manage.py shell` | Mở Python shell trong ngữ cảnh Django |

**`manage.py` là cấu trúc phổ biến/tiêu chuẩn của một Django project, nhưng không phải thành phần bắt buộc tuyệt đối.** Có thể dùng `django-admin` với `DJANGO_SETTINGS_MODULE` được cấu hình đúng.

`manage.py` **không phải chính web server**: nó là điểm vào để Django xử lý các lệnh quản trị. Khi deploy production, thông thường ứng dụng được phục vụ qua ASGI/WSGI server và reverse proxy phù hợp.

## 3. Nội dung `manage.py` và giải thích

```python
#!/usr/bin/env python3

import os
import sys


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings",
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

**Giải thích từng phần:**

- `#!/usr/bin/env python3`: shebang để xác định trình thông dịch khi chạy file trực tiếp trên hệ Unix (không bắt buộc khi chạy `python manage.py`).
- `import os`: sử dụng biến môi trường, ví dụ `os.environ`.
- `import sys`: lấy tham số được nhập trên dòng lệnh qua `sys.argv`.
- `os.environ.setdefault(...)`: nếu chưa có biến `DJANGO_SETTINGS_MODULE`, đặt mặc định là `config.settings`.
- `config.settings`: tên **Python module** tương ứng với `config/settings.py`, không phải đường dẫn file theo cú pháp `/`.
- `execute_from_command_line(sys.argv)`: chuyển các tham số dòng lệnh sang hệ thống quản lý của Django.
- `if __name__ == "__main__":`: chỉ gọi `main()` khi thực thi file trực tiếp.

Ví dụ:

```bash
python manage.py runserver 8000
```

Khi đó, `sys.argv` gần tương đương:

```python
["manage.py", "runserver", "8000"]
```

Luồng xử lý:

```text
Terminal
  -> python manage.py runserver 8000
  -> main()
  -> DJANGO_SETTINGS_MODULE = config.settings (nếu chưa đặt)
  -> execute_from_command_line(sys.argv)
  -> Django xử lý lệnh runserver
  -> khởi tạo development server nếu cấu hình hợp lệ
```

## 4. Kiểm thử: Phân biệt đúng ý nghĩa từng lệnh

Đã chạy:

```bash
python -m py_compile manage.py
```

Không có output hoặc traceback nghĩa là **Python biên dịch được cú pháp file**. Tuy nhiên, đây **chưa phải bằng chứng `manage.py` hoạt động đúng**: một file chỉ chứa comment cũng có thể vượt qua `py_compile`!

Kiểm tra thêm:

```bash
python -m django --version
python manage.py --version
```

Django đang được cài là `5.2.18`; lệnh thứ hai cần được chạy và xác minh trên máy local.

Chưa chạy `runserver` nếu chưa tạo đầy đủ cấu hình như `config/settings.py` và `config/urls.py`.

## 5. Cấu trúc Django dự kiến

```text
tech_learn/                  # Git repository
├── manage.py
├── requirements.txt
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                    # Tạo dần khi học
├── templates/
├── static/
└── doc/
    └── 01-django-manage-py-va-gitignore.md
```

Tên package `config` giúp tách cấu hình Django khỏi tên repository `tech_learn`. Các thư mục và file chưa có sẽ được tạo **từng bước**, không cần dựng toàn bộ ngay.

## 6. Kết quả và bước tiếp theo

- [x] Có Git repository tại `~/tech_learn/tech_learn`.
- [x] Đã cài Django 5.2.18 vào môi trường `.techlearn`.
- [x] Đã chạy `python -m py_compile manage.py` không có lỗi cú pháp.
- [ ] Xác minh Git ignore `.techlearn/` và không tracking file bên trong.
- [ ] Chạy `python manage.py --version` để kiểm tra entrypoint.
- [ ] Bài tiếp theo: tạo package `config`, tìm hiểu và tự viết `settings.py` theo từng nhóm cấu hình.

### Lệnh Git để lưu ghi chú này

```bash
mkdir -p doc
# Lưu file Markdown này vào doc/ trước khi chạy các lệnh sau.
git status --short
git add .gitignore manage.py requirements.txt doc/01-django-manage-py-va-gitignore.md
git diff --cached
# Chỉ commit sau khi xem lại diff và chắc chắn không có thông tin nhạy cảm.
```

---

**Nguyên tắc dự án:** Code local trước, hiểu và kiểm thử từng file, sau đó mới xây LMS, tích hợp sandbox Linux/Network độc lập và triển khai Internet khi có nội dung khóa học đủ tốt.
