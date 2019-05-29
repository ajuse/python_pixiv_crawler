# coding=utf-8

from pixiv_ import Pixiv
import json
import os
from bs4 import BeautifulSoup
import re

class Member_illust:
    def __init__(self):
        self.pixiv = Pixiv()

    def get_Member_illust(self, painter_id):
        if painter_id == None:
            return

        painter_path = self.pixiv.load_path + painter_id
        painter_all_url = "https://www.pixiv.net/ajax/user/" + painter_id + "/profile/all"

        if os.path.exists(painter_path) == False:
            os.mkdir(painter_path)

        obj = json.loads(self.pixiv.get_Html(painter_all_url))
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

                img_file = self.pixiv.download_Img(img_url, page_url, painter_id, painter_path) 

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

        print("Already get all pictures of ", painter_id)

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
            illustrators = illustrator_soup.find_all(class_="userdata")
            illustrator_list = re.findall(re.compile('data-user_id="(.*?)"', re.S), str(illustrators))

            all_illustrator_list += illustrator_list

        return all_illustrator_list

    def get_bookmask_all_illustrator(self):
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
            self.get_Member_illust(i)

    def start(self):
        if self.pixiv.login():
            # self.get_Member_illust('3188698')
            self.get_bookmask_all_illustrator()

if __name__ == "__main__":
    Member_illust().start()
