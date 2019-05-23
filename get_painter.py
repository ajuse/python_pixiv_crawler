# coding=utf-8

from pixiv_ import Pixiv
import json
import os


class Member_illust:
    def __init__(self):
        self.pixiv = Pixiv()  # 实例化Pixiv
        self.se = self.pixiv.se  # 传递se3984129
        self.uid = "12539859"
        self.pixiv.load_path = "/Users/luoyunfu/Downloads/pixivpic/" + self.uid + "/"
        self.all_url = "https://www.pixiv.net/ajax/user/" + self.uid + "/profile/all"  # 获取所有插图作品目录
        self.medium_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="  # 获取插图主页的url

    def get_Member_illust(self):
        if os.path.exists(self.pixiv.load_path) == False:
            os.mkdir(self.pixiv.load_path)

        obj = json.loads(self.pixiv.get_Html(self.all_url))
        illusts = obj["body"]["illusts"]

        if illusts == None:
            print("获取作品目录失败")
            return
        print("已获取所有插画作品")

        list = []

        # 获取已下载的图片id并保存到list，防止再次下载
        for file in os.listdir(self.pixiv.load_path):
            list.append(file.replace(".jpg", ""))  # ！！！有可能是png图片，就不能筛除了

        for illust in illusts:
            if illust in list:
                continue

            page_url = self.medium_url + illust
            img_url = self.pixiv.get_Imgs_Url(page_url)

            num = 1
            try_times = 0
            while True:
                print("downloading url: ", img_url)

                img_file = self.pixiv.download_Img(img_url, page_url, illust)

                if img_file == None:
                    print("下载失败", illust)
                    if try_times == 1:
                        break
                    else:
                        try_times += 1
                        continue
                else:
                    try_times = 0

                img_url = img_url[:67] + str(num) + img_url[-4:]
                num += 1

        print("已获取排行榜数据")

    def start(self):
        if self.pixiv.login():
            self.get_Member_illust()


if __name__ == "__main__":
    Member_illust().start()
