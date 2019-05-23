# coding=utf-8
import requests
from bs4 import BeautifulSoup
import os
import time
import json
import config


class Pixiv:

    def __init__(self):
        self.se = requests.session()
        self.base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.main_url = 'http://www.pixiv.net'

        self.proxies = {'http': 'socks5://127.0.0.1:1086',
                        'https': 'socks5://127.0.0.1:1086'}

        self.headers = {
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.pixiv_id = config.pixiv_username
        self.password = config.pixiv_passwd
        self.post_key = []
        self.return_to = 'http://www.pixiv.net/'
        self.load_path = '/Users/luoyunfu/Downloads/pixivpic/'

    def login(self):
        post_key_html = self.se.get(self.base_url, headers=self.headers,
                                    proxies=self.proxies).text  # 登陆前获取存在post_key的页面
        post_key_soup = BeautifulSoup(post_key_html, 'lxml')
        self.post_key = post_key_soup.find('input')['value']  # 从html中解析出post_key

        data = {
            'pixiv_id': self.pixiv_id,
            'password': self.password,
            'return_to': self.return_to,
            'post_key': self.post_key
        }

        try:
            resp = self.se.post(self.login_url, data=data, headers=self.headers, proxies=self.proxies)
            if resp.status_code == 200:
                if "success" in str(resp.content, encoding='utf-8'):
                    print("登陆成功")
                    return True  # 返回登陆成功
                else:
                    print("登陆失败" + json.loads(resp.content)["body"]["validation_errors"]["pixiv_id"])  # 输出错误信息

        except Exception as e:
            print("登录连接产生异常" + str(e))

        return False  # 登陆失败

    def download_Img(self, img_url, referer, title):
        src = img_url
        src_headers = self.headers
        src_headers['Referer'] = referer  # 增加一个referer,否则会403,referer
        try:
            html = requests.get(src, headers=src_headers, proxies=self.proxies)
            print(html)
            if "[200]" not in str(html):
                return None
            img = html.content

        except:  # 有时候会发生错误导致不能获取图片.直接跳过这张图吧
            print('下载图片失败: ', img_url)
            return None

        if os.path.exists(os.path.join(self.load_path, title + '.jpg')):
            for i in range(1, 100):
                if not os.path.exists(os.path.join(self.load_path, title + str(i) + '.jpg')):
                    title = title + str(i)
                    break
        # 如果重名了,就加上一个数字
        # !!! 此处不能处理png为后缀的图片，最好将url切片后命名为图片名称保存

        print('正在保存名字为: ' + title + ' 的图片')
        with open(os.path.join(self.load_path, title + '.jpg'), 'ab') as f:  # 图片以二进制的方式写入文件
            f.write(img)
        print('保存该图片完毕')
        return os.path.join(self.load_path, title + '.jpg')

    def get_Imgs_Url(self, img_url):
        html = self.get_Html(img_url)  # 获取图片的html
        img_soup = BeautifulSoup(html, 'lxml')
        img_soup_str = str(img_soup)
        if "original" not in img_soup_str:
            return None
        img_info = img_soup_str[img_soup_str.index("original") + 11: img_soup_str.index("tags") - 4]
        return img_info.replace("\\", "")

    def get_Html(self, url, timeout=3, num_entries=5):
        try:
            return self.se.get(url, headers=self.headers, timeout=timeout, proxies=self.proxies).content
        except:
            if num_entries > 0:
                print(url + "页面失败,3秒后将会重新获取")
                time.sleep(3)
                return self.get_Html(url, timeout, num_entries=num_entries - 1)
            else:
                print('获取网页失败: ', url)

    def mkdir(self, path):
        path = path.strip()
        is_exist = os.path.exists(os.path.join(self.load_path, path))
        if not is_exist:
            print('创建一个名字为 ' + path + ' 的文件夹')
            os.makedirs(os.path.join(self.load_path, path))
            os.chdir(os.path.join(self.load_path, path))
            return True
        else:
            print('名字为 ' + path + ' 的文件夹已经存在')
            os.chdir(os.path.join(self.load_path, path))
            return False


if __name__ == "__main__":
    pixiv = Pixiv()
    pixiv.login()
