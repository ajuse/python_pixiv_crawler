# coding=utf-8

from pixiv_ import Pixiv
import json
import os


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

        print("Already got all contents of illust")

        for illust in illusts:
            page_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + illust
            img_url = self.pixiv.get_Imgs_Url(page_url)
            pic_date = img_url[37:47].replace('/', '')

            # download images from deadline
            if self.pixiv.deadline != None and self.pixiv.deadline > pic_date:
                break

            num = 1
            try_times = 0
            while True:
                print("downloading url: ", img_url)

                img_file = self.pixiv.download_Img(img_url, page_url, painter_id)

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

    def start(self):
        if self.pixiv.login():
            self.get_Member_illust('6662895')


if __name__ == "__main__":
    Member_illust().start()
