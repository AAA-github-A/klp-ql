# 苦力怕论坛自动签到脚本

原项目 [Github](https://github.com/xyz8848/KLPBBS_auto_sign_in) [Gitee](https://gitee.com/xyz8848/KLPBBS_auto_sign_in)

## 修改部分
- 不再使用GitHub Action
- 适配青龙
- 支持多账号

## 如何使用
青龙->订阅管理->创建订阅

```
名称:随意  
类型:公开仓库  
链接:https://github.com/AAA-github-A/klp-ql.git  
定时类型:crontab  
定时规则:0 0 * * *
```
保存后，点击运行按钮，运行拉库  

拉库成功后会自动添加定时任务

环境变量中添加[`USERNAME`](/docs/secrets.md#USERNAME),[`PASSWORD`](/docs/secrets.md#PASSWORD)/[`ACCOUNTS`](/docs/secrets.md#ACCOUNTS)

其余功能使用方法同上，参考[Gitee](https://gitee.com/xyz8848/KLPBBS_auto_sign_in)和[secrets](/docs/secrets.md)

仅Telegram、邮箱通知和签到经过测试，其余部分是否可用未知
