#!/bin/bash
set -euo pipefail

LAB_USERNAME="${LAB_USERNAME:-lab}"

# Kiểm tra tên tài khoản Linux hợp lệ.
if [[ ! "$LAB_USERNAME" =~ ^[a-z_][a-z0-9_-]{0,30}$ ]]; then
    echo "Invalid Linux username" >&2
    exit 1
fi

# Không cho trùng tài khoản hệ thống khác.
if [[ "$LAB_USERNAME" != "lab" ]] &&
   grep -q "^${LAB_USERNAME}:" /etc/passwd; then
    echo "Reserved Linux username" >&2
    exit 1
fi

# Tạo các file ánh xạ trong bộ nhớ tạm.
umask 077

export NSS_WRAPPER_PASSWD
export NSS_WRAPPER_GROUP

NSS_WRAPPER_PASSWD=$(mktemp /tmp/lab-passwd.XXXXXX)
NSS_WRAPPER_GROUP=$(mktemp /tmp/lab-group.XXXXXX)

# Giữ tài khoản hệ thống, thay tên user lab.
grep -v '^lab:' /etc/passwd > "$NSS_WRAPPER_PASSWD"
grep -v '^lab:' /etc/group > "$NSS_WRAPPER_GROUP"

printf '%s:x:10001:10001:TechLearn Student:/home/%s:/bin/bash\n' \
    "$LAB_USERNAME" "$LAB_USERNAME" \
    >> "$NSS_WRAPPER_PASSWD"

printf '%s:x:10001:\n' "$LAB_USERNAME" \
    >> "$NSS_WRAPPER_GROUP"

export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libnss_wrapper.so

export HOME="/home/$LAB_USERNAME"
export USER="$LAB_USERNAME"
export LOGNAME="$LAB_USERNAME"

mkdir -p "$HOME"
chmod 700 "$HOME"

cd "$HOME"

export PS1='\u@techlearn:\w\$ '

exec /bin/bash --noprofile --norc -i
