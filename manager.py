# manager.py is a command-line utility that lets you interact with this Django project in various ways. You can read all the details about manage.py in the Django documentation.

#!/usr/bin/env python3
import os # Làm việc với biến môi trường
import sys # Đọc tham số dòng lệnh

def main(): 
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", # Chỉ định module setting của Django
        "config.settings" # Trỏ đến file settings.py trong thư mục config
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv) # Thực thi lệnh quản lý Django với các tham số dòng lệnh được truyền vào

if __name__ == "__main__":
    main()