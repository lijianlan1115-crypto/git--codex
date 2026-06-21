#!/bin/zsh

MODE="$1"
ENCODED_PROMPT="$2"
REPO_DIR="$3"

if [ -z "$MODE" ]; then
  MODE="analyze"
fi

if [ -z "$REPO_DIR" ]; then
  REPO_DIR="/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流/repos/hotel--ota-ai"
fi

export HOME="/Users/jelly"
export PATH="/opt/homebrew/bin:/Users/jelly/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export USER="jelly"
export LOGNAME="jelly"
export SHELL="/bin/zsh"
export TERM="xterm-256color"
export LANG="zh_CN.UTF-8"
export LC_ALL="zh_CN.UTF-8"

PROMPT=$(echo "$ENCODED_PROMPT" | base64 --decode)

cd "$REPO_DIR" || exit 2

if [ "$MODE" = "apply" ]; then
  /Users/jelly/.npm-global/bin/codex exec --sandbox workspace-write --skip-git-repo-check "$PROMPT"
else
  /Users/jelly/.npm-global/bin/codex exec --sandbox read-only --skip-git-repo-check "$PROMPT"
fi
