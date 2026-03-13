#!/bin/bash
# 鸿蒙智行每日简报脚本
# 每天16:00收集最新资讯并发送邮件

SKILL_DIR="/home/sandbox/.openclaw/workspace/skills"
WORKSPACE="/home/sandbox/.openclaw/workspace"
LOG_FILE="$WORKSPACE/memory/hongmeng-report.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "========== 开始执行鸿蒙智行每日简报 =========="

# 搜索最新资讯
log "正在搜索鸿蒙智行最新资讯..."
SEARCH_RESULT=$(cd "$SKILL_DIR/xiaoyi-web-search" && node ./scripts/search.js "鸿蒙智行最新新闻 $(date '+%Y年%m月')" -n 8 2>&1)
log "搜索完成"

# 生成简报内容
TODAY=$(date '+%Y年%m月%d日')
SUBJECT="鸿蒙智行每日资讯简报 - $TODAY"

# 构建邮件内容
BODY="【鸿蒙智行每日资讯简报】
日期：$TODAY

$SEARCH_RESULT

========================================
本简报由小艺Claw自动生成
如需取消订阅，请回复"取消鸿蒙简报"
"

# 发送邮件
log "正在发送邮件..."
SEND_RESULT=$(cd "$SKILL_DIR/smtp-mailer" && node scripts/send-mail.js send 3512258913@qq.com "$SUBJECT" "$BODY" 2>&1)
log "邮件发送结果: $SEND_RESULT"

log "========== 简报任务完成 =========="
