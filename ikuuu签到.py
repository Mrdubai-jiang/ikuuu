#cron: 23 0 * * *
#new Env('ikuuu签到');
#地址：https://ikuuu.one/
#环境变量 bd_ikuuu = 邮箱#密码
#多账号新建变量或者用 & 分开

import time
import requests
from os import environ
from bs4 import BeautifulSoup


# 获取环境变量
def get_environ(key, default="", output=True):
    def no_read():
        if output:
            print(f"未填写环境变量 {key} 请添加")
            exit(0)
        return default
    
    return environ.get(key) if environ.get(key) else no_read()


class ikuuu():
    def __init__(self, ck):
        self.msg = ''
        self.ck = ck
        self.cks = ""
        self.session = requests.Session()  # 使用 Session 保持会话

    def sign(self):
        time.sleep(0.5)
        url = "https://ikuuu.one/user/checkin"
        url1 = 'https://ikuuu.one/user'
        login_url = 'https://ikuuu.one/auth/login'

        login_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ikuuu.one',
            'Referer': 'https://ikuuu.one/auth/login',
        }

        data = {
            'email': self.ck[0],
            'passwd': self.ck[1],
        }
        
        # 使用 Session 发送请求
        response = self.session.post(login_url, headers=login_header, data=data)
        
        if response.status_code != 200:
            xx = f"[登录]：登录请求失败，状态码：{response.status_code}，请检查网络或账号密码：{self.ck}\n\n"
            print(xx)
            self.msg += xx
            return self.msg
        
        cookies_dict = response.cookies.get_dict()
        self.cks = '; '.join([f"{key}={value}" for key, value in cookies_dict.items()])

        headers = {
            'Cookie': self.cks,
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        time.sleep(0.5)
        r = self.session.post(url, headers=headers)
        time.sleep(0.5)
        r1 = self.session.get(url1, headers=headers)
        
        try:
            soup = BeautifulSoup(r1.text, 'html.parser')
            bs = soup.find('span', {'class': 'counter'})
            syll = bs.text
            dl = soup.find('div', {'class': 'd-sm-none d-lg-inline-block'})
            name = dl.text.strip()
        except Exception as e:
            xx = f"[登录]：解析失败，请检查ck有效性：{self.ck}，错误信息：{str(e)}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

        if r.status_code != 200:
            xx = f"[登录]：{name}\n[签到]：请求失败，请检查网络或ck有效性：{self.ck}\n\n"
            print(xx)
            self.msg += xx
            return self.msg
        
        try:
            if "已经签到" in r.json()['msg']:
                xx = f"[登录]：{name}\n[签到]：{r.json()['msg']}\n[流量]：{syll}GB\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            elif "获得" in r.json()['msg']:
                xx = f"[登录]：{name}\n[签到]：{r.json()['msg']}\n[流量]：{syll}GB\n\n"
                print(xx)
                self.msg += xx
                return self.msg
            else:
                xx = f"[登录]：未知错误，请检查网络或ck有效性：{self.ck}\n\n"
                print(xx)
                self.msg += xx
                return self.msg
        except Exception as e:
            xx = f"[登录]：解析响应失败，请检查网络或ck有效性：{self.ck}，错误信息：{str(e)}\n\n"
            print(xx)
            self.msg += xx
            return self.msg

    def get_sign_msg(self):
        return self.sign()


if __name__ == '__main__':
    token = get_environ("bd_ikuuu")
    msg = ''
    cks = token.split("&")
    print("检测到{}个ck记录\n开始ikuuu签到\n".format(len(cks)))
    for ck_all in cks:
        ck = ck_all.split("#")
        run = ikuuu(ck)
        msg += run.get_sign_msg()
    
    # 内置wxpusher配置
    wxpusher_app_token = "AT_TGW73HfYFjoB38LzP1cFpvLjgzpuaNAu"
    wxpusher_uids = ["UID_AOAqOlcllOdb18CQn06fDcqxlMAR"]
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": wxpusher_app_token,
        "content": msg,
        "summary": "ikuuu签到通知",
        "contentType": 1,
        "topicIds": [],
        "uids": wxpusher_uids,
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        if response.status_code == 200 and result.get("code") == 1000:
            print("wxpusher通知发送成功")
        else:
            print(f"wxpusher通知发送失败: {result.get('msg')}")
    except Exception as e:
        print(f"发送wxpusher通知时出错: {e}")
