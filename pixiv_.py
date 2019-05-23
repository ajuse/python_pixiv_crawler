# coding=utf-8
import requests
from bs4 import BeautifulSoup
import os
import time
import json
import config

# creat a class of pixiv
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
        post_key_html = self.se.get(self.base_url, headers=self.headers, proxies=self.proxies).text
        post_key_soup = BeautifulSoup(post_key_html, 'lxml')
        # get post_key from html
        self.post_key = post_key_soup.find('input')['value']

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
                    print("login success...")
                    return True
                else:
                    print("login fail" + json.loads(resp.content)["body"]["validation_errors"]["pixiv_id"])  # 输出错误信息

        except Exception as e:
            print("login error: " + str(e))

        return False

    def download_Img(self, img_url, referer, title):
        src = img_url
        src_headers = self.headers
        src_headers['Referer'] = referer  # there must have a referer
        try:
            html = requests.get(src, headers=src_headers, proxies=self.proxies)
            # check html is response 200
            if "[200]" not in str(html):
                return None
            img = html.content

        except:  # something is wrong and give up this picture
            print('download failed: ', img_url)
            return None

        if os.path.exists(os.path.join(self.load_path, title + '.jpg')):
            for i in range(1, 100):
                if not os.path.exists(os.path.join(self.load_path, title + str(i) + '.jpg')):
                    title = title + str(i)
                    break
        # Note! this can't deal with '.png'

        print('downloading: ' + title)
        with open(os.path.join(self.load_path, title + '.jpg'), 'ab') as f:
            f.write(img)

        return os.path.join(self.load_path, title + '.jpg')

    def get_Imgs_Url(self, img_url):
        html = self.get_Html(img_url)
        img_soup = BeautifulSoup(html, 'lxml')
        img_soup_str = str(img_soup)
        if "original" not in img_soup_str:
            return None
        img_info = img_soup_str[img_soup_str.index("original") + 11: img_soup_str.index("tags") - 4]
        return img_info.replace("\\", "")

    def get_Html(self, url, timeout=3, num_entries=3):
        try:
            return self.se.get(url, headers=self.headers, timeout=timeout, proxies=self.proxies).content
        except:
            if num_entries > 0:
                print(url + ' fail, will reload after ' + timeout + ' second')
                time.sleep(timeout)
                return self.get_Html(url, timeout, num_entries=num_entries - 1)
            else:
                print('get html fail: ', url)

    def mkdir(self, path):
        path = path.strip()
        is_exist = os.path.exists(os.path.join(self.load_path, path))
        if not is_exist:
            print('creat ' + path + ' directory')
            os.makedirs(os.path.join(self.load_path, path))
            os.chdir(os.path.join(self.load_path, path))
            return True
        else:
            print(path + ' directory already exists')
            os.chdir(os.path.join(self.load_path, path))
            return False


if __name__ == "__main__":
    pixiv = Pixiv()
    pixiv.login()
