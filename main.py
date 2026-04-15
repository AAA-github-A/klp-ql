"""
GitHub: https://github.com/xyz8848/KLPBBS_auto_sign_in
Gitee: https://gitee.com/xyz8848/KLPBBS_auto_sign_in

cron: 0 6 * * *
new Env("klp自动签到")
"""

import os
import sys
import logging
import http.cookiejar
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 依赖检查模块
# ==========================================
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误：检测到缺少必要依赖 requests 或 beautifulsoup4。")
    print("请在青龙面板的【依赖管理】->【Python3】中添加以上两个依赖后再运行。")
    sys.exit(1)


# ==========================================
# 全局配置读取模块
# ==========================================
PROJECT_URL = "https://github.com/A-cookie-A/klp-ql"
accounts = []

# 获取环境变量
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
accounts_str = os.environ.get("ACCOUNTS", "")

# 1. 处理单账号配置
if username and password:
    accounts.append({"username": username, "password": password})

# 2. 处理多账号配置
if accounts_str:
    account_pairs = accounts_str.split(';')
    for pair in account_pairs:
        if ':' in pair:
            # 使用 split(':', 1) 防止密码中包含冒号导致解析错误
            user, pwd = pair.split(':', 1)
            accounts.append({"username": user.strip(), "password": pwd.strip()})

if not accounts:
    logging.error("未配置任何账号，请设置 USERNAME/PASSWORD 或 ACCOUNTS 环境变量")
    sys.exit(1)

# 日志及环境配置
debug = int(os.environ.get("DEBUG") or 0)
log_level = logging.DEBUG if debug == 1 else logging.INFO
logging.basicConfig(level=log_level, format="[%(levelname)s] [%(asctime)s] %(message)s")
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

# ==========================================
# 通知参数配置
# ==========================================
mail_enable = int(os.environ.get("MAIL_ENABLE") or 0)
mail_host = os.environ.get("MAIL_HOST")
mail_port = int(os.environ.get("MAIL_PORT") or 0)
mail_username = os.environ.get("MAIL_USERNAME")
mail_password = os.environ.get("MAIL_PASSWORD")
mail_to = os.environ.get("MAIL_TO") or ""

wechat_enable = int(os.environ.get("WECHAT_ENABLE") or 0)
wechat_webhook = os.environ.get("WECHAT_WEBHOOK")
wechat_mentioned = os.environ.get("WECHAT_MENTIONED") or ""

serverchan_enable = int(os.environ.get("SERVERCHAN_ENABLE") or 0)
serverchan_key = os.environ.get("SERVERCHAN_KEY")

tg_enable = int(os.environ.get("TG_ENABLE") or 0)
tg_token = os.environ.get("TG_TOKEN")
tg_chat_id = os.environ.get("TG_CHAT_ID")

ntfy_enable = int(os.environ.get("NTFY_ENABLE") or 0)
ntfy_url = os.environ.get("NTFY_URL") or "https://ntfy.sh"
ntfy_topic = os.environ.get("NTFY_TOPIC")
ntfy_username = os.environ.get("NTFY_USERNAME")
ntfy_password = os.environ.get("NTFY_PASSWORD")
ntfy_token = os.environ.get("NTFY_TOKEN")


# ==========================================
# 核心功能模块
# ==========================================
def login(username_str: str, password_str: str):
    """
    模拟登录苦力怕论坛并获取 Cookie Session
    
    :param username_str: 论坛用户名
    :param password_str: 论坛密码
    :return: 包含登录状态的 session 和 header，若失败则返回 (None, None)
    """
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookieJar()
    header = {
        "origin": "https://klpbbs.com",
        "Referer": "https://klpbbs.com/",
        "User-Agent": userAgent,
    }
    post_url = "https://klpbbs.com/member.php?mod=logging&action=login&loginsubmit=yes"
    post_data = {"username": username_str, "password": password_str}

    try:
        response = session.post(post_url, data=post_data, headers=header, timeout=20)
        logging.debug(f"登录响应状态码: {response.status_code}")
        # 保存 Cookie 以备后续请求使用
        header["Cookie"] = "; ".join([f"{c.name}={c.value}" for c in session.cookies])
        return session, header
    except Exception as e:
        logging.error(f"登录请求发生异常: {e}")
        return None, None


def get_url(session, header):
    """
    访问首页获取签到链接
    
    :param session: 请求会话实例
    :param header: 请求头
    :return: 签到链接字符串，或 "already_signed"，若解析失败则返回 None
    """
    try:
        html_source = session.get("https://klpbbs.com/", headers=header, timeout=20)
        soup = BeautifulSoup(html_source.text, "html.parser")
        
        # 判断是否带有已签到的样式类
        if soup.find("a", class_="midaben_signpanel JD_sign visted"):
            return "already_signed"
        
        # 获取签到触发的动态链接
        a_tag = soup.find("a", class_="midaben_signpanel JD_sign")
        if a_tag:
            href = a_tag["href"]
            # 若链接指向登录页，说明 Cookie 失效
            if "logging&action=login" in href:
                logging.warning("Cookie失效，被重定向至登录页面")
                return None
            return "https://klpbbs.com/" + href
    except Exception as e:
        logging.error(f"解析页面失败: {e}")
    return None


def sign_in(sign_url: str, session, header):
    """
    执行签到网络请求
    """
    if sign_url and sign_url != "already_signed":
        try:
            session.get(sign_url, headers=header, timeout=20)
        except Exception as e:
            logging.error(f"执行签到请求失败: {e}")


def is_sign_in(session, header) -> bool:
    """
    校验签到动作是否成功生效
    
    :return: 成功返回 True，失败或异常返回 False
    """
    try:
        html_source = session.get("https://klpbbs.com/", headers=header, timeout=20)
        soup = BeautifulSoup(html_source.text, "html.parser")
        return soup.find("a", class_="midaben_signpanel JD_sign visted") is not None
    except Exception as e:
        logging.error(f"校验签到状态异常: {e}")
        return False


# ==========================================
# 消息推送模块
# ==========================================
def normalize_domain(domain: str) -> str:
    """规范化域名地址，确保包含 http 协议头部且以斜杠结尾"""
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    return domain.rstrip("/") + "/"


def email_notice(msg: str):
    """发送邮件通知"""
    message = MIMEMultipart()
    message["From"] = mail_username
    message["To"] = mail_to
    message["Subject"] = "苦力怕论坛签到通知"
    
    # 替换换行符并拼接 HTML 格式体
    msg_html = msg.replace('\n', '<br>')
    body = f"<h1>苦力怕论坛自动签到</h1>{msg_html}<br><br>Powered by <a href='{PROJECT_URL}'>项目地址</a>"
    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(mail_host, mail_port)
        server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(message)
        logging.info("邮件发送成功")
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")


def wechat_notice(msg: str):
    """发送企业微信通知"""
    url = wechat_webhook
    # 兼容用户仅填写 key 的情况，自动补全协议地址
    if url and not url.startswith(("http://", "https://")):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={url}"

    data = {
        "msgtype": "text",
        "text": {
            # 企微为纯文本推送，直接附上明文链接使其可点击
            "content": f"苦力怕论坛自动签到\n\n{msg}\n\nPowered by {PROJECT_URL}",
            "mentioned_list": wechat_mentioned,
        }
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logging.info("企业微信通知发送成功")
        else:
            logging.error(f"企业微信通知发送失败，状态码：{response.status_code}")
    except Exception as e:
        logging.error(f"企业微信推送异常: {e}")


def serverchan_notice(msg: str):
    """发送 Server 酱通知"""
    url = f"https://sctapi.ftqq.com/{serverchan_key}.send"
    data = {"title": "苦力怕论坛签到通知", "desp": msg}
    try:
        requests.post(url, data=data, timeout=10)
        logging.info("Server酱消息发送成功")
    except Exception as e:
        logging.error(f"Server酱消息发送异常: {e}")


def tg_notice(msg: str):
    """发送 Telegram 机器人通知"""
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = {
        "chat_id": tg_chat_id,
        # TG 支持 HTML 解析，这里构造可点击的超链接
        "text": f"<b>苦力怕论坛自动签到</b>\n\n{msg}\n\n<a href='{PROJECT_URL}'>项目地址</a>",
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
        logging.info("Telegram消息发送成功")
    except Exception as e:
        logging.error(f"Telegram消息发送异常: {e}")


def ntfy_notice(msg: str):
    """发送 Ntfy 通知"""
    auth = None
    if ntfy_username:
        auth = requests.auth.HTTPBasicAuth(ntfy_username, ntfy_password)
    elif ntfy_token:
        auth = requests.auth.HTTPBasicAuth("", ntfy_token)

    url = f"{normalize_domain(ntfy_url)}{ntfy_topic}"
    # Ntfy 通常处理纯文本
    full_msg = f"{msg}\n\nPowered by {PROJECT_URL}"
    headers = {"Title": "苦力怕论坛自动签到通知"}
    
    try:
        requests.post(url, data=full_msg.encode("utf-8"), headers=headers, auth=auth, timeout=10)
        logging.info("Ntfy消息发送成功")
    except Exception as e:
        logging.error(f"Ntfy消息发送异常: {e}")


def notice(msg: str):
    """路由通知分发器"""
    if mail_enable == 1: email_notice(msg)
    if wechat_enable == 1: wechat_notice(msg)
    if serverchan_enable == 1: serverchan_notice(msg)
    if tg_enable == 1: tg_notice(msg)
    if ntfy_enable == 1: ntfy_notice(msg)


# ==========================================
# 任务入口
# ==========================================
if __name__ == "__main__":
    logging.info(f"开始执行签到任务，账号总数: {len(accounts)}")
    results = []

    for account in accounts:
        u = account["username"]
        p = account["password"]
        logging.info(f"正在处理: {u}")
        
        try:
            # 1. 登录
            session, header = login(u, p)
            if not session:
                results.append(f"账号 {u}: 登录失败")
                continue

            # 2. 获取链接
            url = get_url(session, header)
            if url == "already_signed":
                results.append(f"账号 {u}: 今日已签到")
            elif url:
                # 3. 签到并验证
                sign_in(url, session, header)
                if is_sign_in(session, header):
                    results.append(f"账号 {u}: 签到成功")
                else:
                    results.append(f"账号 {u}: 签到验证失败")
            else:
                results.append(f"账号 {u}: 未能获取签到链接")
                
        except Exception as e:
            results.append(f"账号 {u}: 运行异常 - {str(e)}")

    # 4. 汇总及推送
    summary = "\n".join(results)
    logging.info(f"汇总结果:\n{summary}")
    
    if results:
        notice(f"苦力怕论坛签到任务完成！\n\n{summary}")
