#!/usr/bin/env bash
# 一键提交并推送到 GitHub
# 用法：bash scripts/git_sync.sh "提交说明"
# 说明：使用本机安装的 Git（C:\Program Files\Git），它保存了 GitHub 登录凭据；
#       ShunCode 自带的 git 无法读取凭据，推送会失败。
set -e
G="/c/Program Files/Git/cmd/git.exe"
[ -x "$G" ] || G=git
MSG=${1:-"chore: sync experiment results"}
"$G" add -A
if "$G" diff --cached --quiet; then
  echo "没有新的改动需要提交"
else
  "$G" commit -q -m "$MSG"
  echo "已提交：$("$G" log --oneline -1)"
fi
GCM_INTERACTIVE=never GIT_TERMINAL_PROMPT=0 timeout 120 \
  "$G" -c credential.helper= -c credential.helper=manager push origin main 2>&1 | tail -2
"$G" status -sb | head -1
