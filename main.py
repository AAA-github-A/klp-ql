"""
GitHub: https://github.com/xyz8848/KLPBBS_auto_sign_in
Gitee: https://gitee.com/xyz8848/KLPBBS_auto_sign_in

cron:0 6 * * *
new Env("klp自动签到")

"""

# ========== 添加依赖检查 ==========
import os
import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("检测到缺少依赖，正在自动安装...")
    os.system(f"{sys.executable} -m pip install requests beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple")
    print("依赖安装完成，请重新运行脚本")
    sys.exit(1)
# ========== 依赖检查结束 ==========

import http
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from http import cookiejar

# 多账号配置
# 支持两种配置方式：
# 1. USERNAME/PASSWORD（单账号）
# 2. ACCOUNTS（多账号，格式：账号1:密码1;账号2:密码2）
accounts = []
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

if username and password:
    accounts.append({"username": username, "password": password})

accounts_str = os.environ.get("ACCOUNTS", "")
if accounts_str:
    account_pairs = accounts_str.split(';')
    for pair in account_pairs:
        if ':' in pair:
            user, pwd = pair.split(':', 1)
            accounts.append({"username": user.strip(), "password": pwd.strip()})

if not accounts:
    logging.error("未配置任何账号，请设置 USERNAME/PASSWORD 或 ACCOUNTS 环境变量")
    exit(1)

switch_user = int(os.environ.get("SWITCH_USER") or 0)
renewal_vip = int(os.environ.get("RENEWAL_VIP") or 0)
renewal_svip = int(os.environ.get("RENEWAL_SVIP") or 0)

debug = int(os.environ.get("DEBUG") or 0)

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

# 设置日志级别和格式
if debug == 1:
    logging.basicConfig(
        level=logging.DEBUG, format="[%(levelname)s] [%(asctime)s] %(message)s"
    )
    logging.info("Debug mode enabled.")
else:
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s"
    )
    logging.info("Debug mode disabled.")

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.81"


def login(username: str, password: str):
    """登录苦力怕论坛"""
    session = requests.session()
    session.cookies = http.cookiejar.LWPCookieJar()

    header = {
        "origin": "https://klpbbs.com",
        "Referer": "https://klpbbs.com/",
        "User-Agent": userAgent,
    }

    post_url = "https://klpbbs.com/member.php?mod=logging&action=login&loginsubmit=yes"
    post_data = {"username": username, "password": password}

    response_res = session.post(post_url, data=post_data, headers=header)
    logging.debug(f"statusCode = {response_res.status_code}")

    header["Cookie"] = "; ".join(
        [f"{cookie.name}={cookie.value}" for cookie in session.cookies]
    )
    return session, header


def get_url(session, header):
    """获取签到链接"""
    html_source = session.get("https://klpbbs.com/", headers=header)
    soup = BeautifulSoup(html_source.text, "html.parser")
    
    # 检查是否已签到
    signed_tag = soup.find("a", class_="midaben_signpanel JD_sign visted")
    if signed_tag is not None and signed_tag.get("href") == "k_misign-sign.html":
        logging.info("今日已签到")
        return "already_signed"
    
    # 查找签到链接
    a_tag = soup.find("a", class_="midaben_signpanel JD_sign")
    if a_tag is not None:
        href_value = a_tag["href"]
        sign_in_url = "https://klpbbs.com/" + href_value
        logging.debug(f"签到链接：{sign_in_url}")

        if sign_in_url == "https://klpbbs.com/member.php?mod=logging&action=login":
            logging.info("签到链接异常（原因：登录失败）")
            return None
        logging.info("已成功获取签到链接")
        return sign_in_url
    return None


def sign_in(sign_in_url: str, session, header):
    """签到"""
    if sign_in_url and sign_in_url != "already_signed":
        session.get(sign_in_url, headers=header)


def is_sign_in(session, header):
    """检测是否签到成功"""
    html_source = session.get("https://klpbbs.com/", headers=header)
    soup = BeautifulSoup(html_source.text, "html.parser")
    a_tag = soup.find("a", class_="midaben_signpanel JD_sign visted")
    if a_tag is not None and a_tag.get("href") == "k_misign-sign.html":
        logging.info("已成功签到")
        return True
    logging.info("签到失败")
    return False


def notice(msg: str):
    """签到后提示"""
    if mail_enable == 1:
        email_notice(msg)
    if wechat_enable == 1:
        wechat_notice(msg)
    if serverchan_enable == 1:
        serverchan_notice(msg)
    if tg_enable == 1:
        tg_notice(msg)
    if ntfy_enable == 1:
        ntfy_notice(msg)


def email_notice(msg: str):
    """邮件通知"""
    message = MIMEMultipart()
    message["From"] = mail_username
    message["To"] = mail_to
    message["Subject"] = "苦力怕论坛签到通知"
    
    msg_html = msg.replace('\n', '<br>')

    body = f"<h1>苦力怕论坛自动签到</h1>{msg_html}<br><br>Powered by <a href='https://github.com/A-cookie-A/klp-ql'>项目地址</a>"
    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(mail_host, mail_port)
        server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(message)
        logging.info("邮件发送成功")
    except smtplib.SMTPException as error:
        logging.info("邮件发送失败")
        logging.error(error)


def wechat_notice(msg: str):
    """企业微信通知"""
    data = {
        "msgtype": "text",
        "text": {
            # 这里的链接已更新为 A-cookie-A
            "content": f"苦力怕论坛自动签到\n\n{msg}\n\nPowered by https://github.com/A-cookie-A/klp-ql",
            "mentioned_list": wechat_mentioned,
        }
    }
    response = requests.post(wechat_webhook, json=data)
    if response.status_code == 200:
        logging.info("企业微信通知发送成功")
    else:
        logging.error(f"企业微信通知发送失败，状态码：{response.status_code}")


def serverchan_notice(msg: str):
    """Server酱通知"""
    url = f"https://sctapi.ftqq.com/{serverchan_key}.send"
    data = {"title": "苦力怕论坛签到通知", "desp": msg}
    try:
        response = requests.post(url, data=data)
        logging.debug(response.text)
        logging.info("Server酱消息发送成功")
    except requests.RequestException as error:
        logging.info("Server酱消息发送失败")
        logging.error(error)


def tg_notice(msg: str):
    """Telegram通知"""
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = {
        "chat_id": tg_chat_id,
        "text": f"<b>苦力怕论坛自动签到</b>\n\n{msg}\n\n<a href='https://github.com/A-cookie-A/klp-ql'>项目地址</a>",
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        logging.debug(response.text)
        logging.info("Telegram消息发送成功")
    except requests.RequestException as error:
        logging.info("Telegram消息发送失败")
        logging.error(error)


def ntfy_notice(msg: str):
    """Ntfy通知"""
    if ntfy_username:
        auth = requests.auth.HTTPBasicAuth(ntfy_username, ntfy_password)
    elif ntfy_token:
        auth = requests.auth.HTTPBasicAuth("", ntfy_token)
    else:
        auth = None

    corrected_url = normalize_domain(ntfy_url)
    url = f"{corrected_url}{ntfy_topic}"
    full_msg = f"{msg}\n\nPowered by https://github.com/A-cookie-A/klp-ql"
    headers = {"Title": "苦力怕论坛自动签到通知"}
    try:
        response = requests.post(url, data=full_msg.encode("utf-8"), headers=headers, auth=auth)
        logging.debug(response.text)
        logging.info("Ntfy消息发送成功")
    except requests.RequestException as error:
        logging.info("Ntfy消息发送失败")
        logging.error(error)


def normalize_domain(domain: str):
    """域名规范化"""
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "https://" + domain
    return domain.rstrip("/") + "/"


if __name__ == "__main__":
    logging.info(f"开始执行苦力怕论坛多账号签到，共 {len(accounts)} 个账号")
    results = []

    for account in accounts:
        username = account["username"]
        password = account["password"]
        logging.info(f"开始处理账号: {username}")

        try:
            session, header = login(username, password)
            url = get_url(session, header)
            
            if url == "already_signed":
                results.append(f"账号 {username}: 今日已签到")
            elif url:
                sign_in(url, session, header)
                success = is_sign_in(session, header)
                if success:
                    results.append(f"账号 {username}: 签到成功")
                else:
                    results.append(f"账号 {username}: 签到失败")
            else:
                results.append(f"账号 {username}: 获取签到链接失败")
        except Exception as e:
            error_msg = f"账号 {username} 出错: {str(e)}"
            logging.error(error_msg)
            results.append(error_msg)

    summary = "\n".join(results)
    logging.info(f"签到汇总:\n{summary}")
    
    # 只在最后发送一次汇总通知
    if results:
        notice(f"苦力怕论坛签到完成！\n\n{summary}")
        
    logging.info("所有账号处理完毕")
