# coding=utf-8

from pixiv import Pixiv
import json
import os
from bs4 import BeautifulSoup
import re
import sys

class Member_illust:
    def __init__(self):
        self.pixiv = Pixiv()

    def get_Member_illust(self, illustrator_id, illustrator_path):
        if illustrator_id == None:
            return

        illustrator_all_url = "https://www.pixiv.net/ajax/user/" + illustrator_id + "/profile/all"

        if os.path.exists(illustrator_path) == False:
            os.mkdir(illustrator_path)

        obj = json.loads(self.pixiv.get_Html(illustrator_all_url))
        illusts = obj["body"]["illusts"]

        if illusts == None:
            print("Get all contents of illust failed!")
            return

        for illust in illusts:
            page_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + illust
            img_url = self.pixiv.get_Imgs_Url(page_url)

            if img_url == None or len(img_url) > 72:
                print('get a None img_url, page_url is ', page_url)
                continue

            pic_date = img_url[37:47].replace('/', '')

            # download images from deadline
            if self.pixiv.deadline != None and self.pixiv.deadline > pic_date:
                return

            num = 1
            try_times = 0
            while True:
                print("downloading url: ", img_url)

                img_file = self.pixiv.download_Img(img_url, page_url, illustrator_path)

                if img_file == 0:  # try it again
                    if try_times == 1:
                        break
                    else:
                        try_times += 1
                        continue
                elif img_file == None:
                    break
                else:
                    try_times = 0

                # https://i.pximg.net/img-original/img/2019/05/24/15/01/48/74877650_p0.png
                # add p0/p1/p2...
                img_url = img_url[:67] + str(num) + img_url[-4:]
                num += 1

        print("Already get all pictures of ", illustrator_id)

    def get_illustrator_list(self, illustrator_url):
        html = self.pixiv.get_Html(illustrator_url)
        soup = BeautifulSoup(html, 'lxml')
        user_num = re.search(re.compile('(\d+)', re.S), str(soup.find_all(class_="count-badge")))

        if user_num == None:
            return None

        illustrator_num = int(user_num.group(1))
        print('There are ', illustrator_num, ' attention illustrators')

        if int(illustrator_num / 48) != 0:
            u_p = int(illustrator_num / 48) + 1
        else:
            u_p = int(illustrator_num / 48)

        # creat a list to save all illustrator id
        all_illustrator_list = []

        for page in range(1, u_p + 1):
            attention_url = illustrator_url + '&p=' + str(page)
            attention_html = self.pixiv.get_Html(attention_url)
            illustrator_soup = BeautifulSoup(attention_html, 'lxml')
            illustrator = illustrator_soup.find_all(class_="userdata")
            illustrator_list = re.findall(re.compile('data-user_id="(.*?)"', re.S), str(illustrator))

            all_illustrator_list += illustrator_list

        return all_illustrator_list

    def get_bookmask_all_illustrator(self, is_update):
        all_uid_list = []
        if os.path.exists('./save_all_bookmask') == False:
            url_base = [
                # hide illustrator
                'https://www.pixiv.net/bookmark.php?type=user&rest=hide',
                # public illustrator
                'https://www.pixiv.net/bookmark.php?type=user&rest=show'
                ]

            for url in url_base:
                all_uid_list += self.get_illustrator_list(url)

            with open('./save_all_bookmask', 'w') as f:
                for uid in all_uid_list:
                    f.write(uid + '\n')
        else:
            with open('./save_all_bookmask', 'r') as f:
                uid = f.readline()
                while uid:
                    all_uid_list.append(uid.strip('\n'))
                    uid = f.readline()

        print(all_uid_list)

        if len(all_uid_list) == 0:
            print('no illustrator to download')
            return

        print('download list:', all_uid_list)

        for i in all_uid_list:
            print('start download illustrator: ', i)
            if is_update == False:
                self.get_Member_illust(i, self.pixiv.load_path + i)
            else:
                self.get_Member_illust(i, self.pixiv.load_path + self.pixiv.deadline)

    def start(self):
        arg = sys.argv[1]

        if self.pixiv.login():
            if arg == 'all':
                print('download all illustrators')
                self.get_bookmask_all_illustrator(False)
            elif arg == 'illustrator':
                uid = sys.argv[2]
                print('download', uid, 'picture')
                self.get_Member_illust(uid, self.pixiv.load_path + uid)
            elif arg == 'update':
                self.pixiv.deadline = sys.argv[2]
                print('download update all bookmask illustrators picture since ', self.pixiv.deadline)
                self.get_bookmask_all_illustrator(True)
            else:
                print('ERROR args')
                return

        # if self.pixiv.login():
            # self.get_Member_illust('3188698')
            #

if __name__ == "__main__":
    Member_illust().start()
