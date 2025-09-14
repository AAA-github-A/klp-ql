# [KLPBBS_auto_sign_in](https://github.com/xyz8848/KLPBBS_auto_sign_in)
## Secrets

### USERNAME
- **描述**：苦力怕论坛用户名
- **必填**：是
- **值型**：字符串
- **示例**：`admin`

### PASSWORD
- **描述**：苦力怕论坛密码
- **必填**：是
- **值型**：字符串
- **示例**：`admin123456`

### SWITCH_USER
- **描述**：当用户组到期时切换至普通用户组（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### RENEWAL_VIP
- **描述**：当 VIP 用户组到期时续费（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### RENEWAL_SVIP
- **描述**：当 SVIP 用户组到期时续费（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### DEBUG
- **描述**：调试模式（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### MAIL_ENABLE
- **描述**：签到后邮件提示（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### MAIL_HOST
- **描述**：SMTP 服务器
- **必填**：否
- **值型**：字符串
- **示例**：`smtp.example.com`

### MAIL_PORT
- **描述**：SMTP 端口
- **必填**：否
- **值型**：整数
- **示例**：`465`

### MAIL_USERNAME
- **描述**：邮箱账号
- **必填**：否
- **值型**：字符串
- **示例**：`admin@example.com`

### MAIL_PASSWORD
- **描述**：邮箱密码
- **必填**：否
- **值型**：字符串
- **示例**：`admin123456`

### MAIL_TO
- **描述**：用于接收通知的邮箱
- **必填**：否
- **值型**：列表
- **示例**：`['admin@example.com']`，`['admin1@example.com', 'admin2@example.com']`

### WECHAT_ENABLE
- **描述**：签到后微信推送（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### WECHAT_WEBHOOK
- **描述**：企业微信机器人的 Webhook 地址
- **必填**：否
- **值型**：字符串
- **示例**：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key`

### WECHAT_MENTIONED
- **描述**：推送信息时 @用户
- **必填**：否
- **值型**：列表
- **示例**：`["@all"]`，`["@user1", "@user2"]`

### TG_ENABLE
- **描述**：签到后 Telegram 通知（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### TG_TOKEN
- **描述**：Telegram Bot Token
- **必填**：否
- **值型**：字符串

### TG_CHAT_ID
- **描述**：Telegram Chat ID
- **必填**：否
- **值型**：字符串

### SERVERCHAN_ENABLE
- **描述**：签到后Server酱提示（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### SERVERCHAN_KEY
- **描述**：Server酱 SendKey
- **必填**：否
- **值型**：字符串

### NTFY_ENABLE
- **描述**：签到后 Ntfy 通知（0=关闭，1=开启）
- **必填**：否
- **值型**：整数
- **示例**：`1`

### NTFY_URL
- **描述**：Ntfy 域名
- **必填**：否
- **值型**：字符串
- **示例**：`https://ntfy.sh/`，`http://ntfy.sh/`，`ntfy.sh`

### NTFY_TOPIC
- **描述**：Ntfy 主题
- **必填**：否
- **值型**：字符串

### NTFY_USERNAME
- **描述**：Ntfy 用户名
- **必填**：否
- **值型**：字符串
- **示例**：`your_ntfy_username`

### NTFY_PASSWORD
- **描述**：Ntfy 密码
- **必填**：否
- **值型**：字符串
- **示例**：`your_ntfy_password`

### NTFY_TOKEN
- **描述**：Ntfy 令牌
- **必填**：否
- **值型**：字符串
- **示例**：`your_ntfy_token`
