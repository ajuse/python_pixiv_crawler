# coding=utf-8

from pixiv_ import Pixiv
import json
import os


class Member_illust:
    def __init__(self):
        self.pixiv = Pixiv()
        self.se = self.pixiv.se
        self.uid = "12539859"
        self.pixiv.load_path = "/Users/luoyunfu/Downloads/pixivpic/" + self.uid + "/"
        # get all contents of illust
        self.all_url = "https://www.pixiv.net/ajax/user/" + self.uid + "/profile/all"
        # get illust main url
        self.medium_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="

    def get_Member_illust(self):
        if os.path.exists(self.pixiv.load_path) == False:
            os.mkdir(self.pixiv.load_path)

        obj = json.loads(self.pixiv.get_Html(self.all_url))
        illusts = obj["body"]["illusts"]

        if illusts == None:
            print("Get all contents of illust failed!")
            return

        print("Already got all contents of illust")

        for illust in illusts:
            page_url = self.medium_url + illust
            img_url = self.pixiv.get_Imgs_Url(page_url)

            num = 1
            try_times = 0
            while True:
                print("downloading url: ", img_url)

                img_file = self.pixiv.download_Img(img_url, page_url, illust)

                if img_file == None:
                    print("download failed : ", illust)
                    if try_times == 1:
                        break
                    else:
                        try_times += 1
                        continue
                else:
                    try_times = 0

                # https://i.pximg.net/img-original/img/2019/05/24/15/01/48/74877650_p0.png
                # add p0/p1/p2...
                img_url = img_url[:67] + str(num) + img_url[-4:]
                num += 1

        print("Already get all pictures of ", self.uid)

    def start(self):
        if self.pixiv.login():
            self.get_Member_illust()


if __name__ == "__main__":
    Member_illust().start()
