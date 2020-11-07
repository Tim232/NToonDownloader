import asyncio
import aiohttp
import aiofiles
import os
from bs4 import BeautifulSoup
import time
from PIL import Image as PILImage


u''.encode('idna')

loop = asyncio.get_event_loop()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}



async def downloads(dir, url):
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as r:
                name = url.split("_")[-1]
                print("Download", name)
                async with aiofiles.open(dir + "/" + name, mode='wb') as f:
                    await f.write(await r.read())
        return True

    except:
        return False


async def crawl(id, no):
    print("# Analyzing {}...".format(no))
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get("https://comic.naver.com/webtoon/detail.nhn?titleId={}&no={}".format(id, no)) as r:
            c = await r.text()
            soup = BeautifulSoup(c, "html.parser") #BeautifulSoup에서 html.parser 사용으로 설정
            title = soup.find("title").text.split("::")[0].rstrip() #HTML에서 title 태그를 가져와서 ::로 나누고, 그 중 처음을 오른쪽 공백 제거 시켜 표시
            div = soup.find_all("img", {"alt":"comic content"}) # HTML에서 Attribute로 alt="comic content"를 가지는 모든 img 태그를 가져온다.
            direc = "downloads/{}".format(title)
            if not os.path.exists(direc):
                os.mkdir(direc)

            direc += "/{}화".format(no)
            if not os.path.exists(direc):
                os.mkdir(direc)
            # imgs = await loop.run_in_executor(None, div.find_all, "img")
    # print(div)
    lists = [asyncio.ensure_future(downloads(direc, i.get('src'))) for i in div]
    # print(lists)
    await asyncio.gather(*lists)

    merge(direc)

    return True


async def multi_crawl(id, no):
    a = no.split("-")
    nos = list(range(int(a[0]), int(a[1]) +1 ))
    
    crawl_list = [asyncio.ensure_future(crawl(id, i)) for i in nos]
    await asyncio.gather(*crawl_list)


def merge(dir):
    image_list = []

    full_width, full_height = 0, 0

    for img in os.listdir(dir):
        im = PILImage.open(dir + "/" + img)

        width, height = im.size

        image_list.append(im)

        full_width = max(full_width, width)

        full_height += height


    canvas = PILImage.new("RGB", (full_width, full_height), "white")

    output_height = 0

    for im in image_list:

        width, height = im.size

        canvas.paste(im, (0, output_height))

        output_height += height

    canvas.save('/'.join(dir.split("/")[:-1]) + "/"+ dir.split("/")[-1]+".jpg")

    for f in os.listdir(dir):
        os.remove(dir+'/'+f)
    os.rmdir(dir)

def main():
    nwebId = int(input("웹툰 코드? :"))
    nwebNo = input("화? (1, 1-3...) :")

    if '-' in nwebNo:
        multiDownload = True
    else:
        multiDownload = False

    try:
        os.mkdir('downloads')
    except FileExistsError:
        pass

    if not multiDownload:
        start = time.time()
        loop.run_until_complete(crawl(nwebId, nwebNo))
        finish = time.time()
        print("## Finished in {}s".format(finish - start))
        input()
    else:
        start = time.time()
        loop.run_until_complete(multi_crawl(nwebId, nwebNo))
        finish = time.time()
        print("## Finished in {}s".format(finish - start))
        input()
               

main()
