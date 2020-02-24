import re
import os
import json

import requests

"""
仅仅学习python网络相关知识使用

@Author  :   yangliangchuang,
@Version :   1.0"
"""

s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'suncreate_login_cookies.txt'

# 全局变量
HOST_ADDR = 'XXX:XX'

class UsernameLogin:

    def __init__(self, username, password):
        """
        账号登录对象
        :param username: 用户名
        :param password: 密码
        """
        # 登录的URL
        self.user_log_url = 'http://' + HOST_ADDR + '/web/frame/login.html'

        # 首页的URL
        self.user_index_url = 'http://' + HOST_ADDR + '/web/frame/index.html'

        # 加班申请的url
        self.add_overtime_url = 'http://' + HOST_ADDR + '/web/admin/ScOvertime/create'

        # 用户名
        self.username = username

        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.password = password

        # 请求超时时间
        self.timeout = 3

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True

        headers = {
            'Host': HOST_ADDR,
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Content-Length': '96',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': HOST_ADDR,
            'Referer':'http://' + HOST_ADDR + '/web/frame/login.html?rtnUrl=http%3A%2F%2F112.31.12.210%3A9139%2Fweb%2Fframe%2Findex.html'
        }

        data = {
            'uer': self.username,
            'userPassword': self.password,
            'submit':'登录',
            'userLogin': self.username
        }

        try:
            response = s.post(self.user_log_url, data=data, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('登录请求，原因：')
            raise e

        # 登录成功，存储cookies
        my_taobao_match = re.search('我的邮箱', response.text)
        if my_taobao_match:
            #print("my_taobao_match: ", my_taobao_match)
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        s.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载全项目登录cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_nick_name(self):
        """
        获取全项目中文用户名
        :return: 中文用户名
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        try:
            response = s.get(self.user_index_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取全项目主页请求失败！原因：')
            raise e
        # 提取全项目中文名
        nick_name_match = re.search(r'<span id="userName">(.*?)<b class="caret"></b></span>', response.text)
        if nick_name_match:
            print('登录全项目成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取全项目中文名失败！response：{}'.format(response.text))

    def submit_overtime_job(self):
        """
        提交加班申请
        :return: 中文用户名
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        }

        data = {
            'dayTime': '2020-02-20',
            'startTime': '17:00',
            'endTime':'21:00',
            'projectName':'xx市雪亮工程项目',
            'projectId':'67E4836A89E3E251FF68F977779C3300',
            'overSubject':'2',
        }
        try:
            response = s.post(self.add_overtime_url, data=data, headers=headers)
            response.raise_for_status()
            print("新增加班申请成功!")
        except Exception as e:
            print('新增加班申请失败，原因：')
            raise e


if __name__ == '__main__':
    # 账号名
    username = 'yangliangchuang'
    # 密码
    password = '123456'
    ul = UsernameLogin(username, password)
    ul.login()
    ul.submit_overtime_job()
