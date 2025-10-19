from DrissionPage import WebPage
from DrissionPage.common import Actions
from time import sleep
import re
import requests
import os
import argparse


def scrape(searchInput, imageCount):
    #Initialize website
    wp = WebPage()
    ac = Actions(wp)
    wp.get('https://www.xiaohongshu.com/')
    ele = wp.ele('#search-input')
    ele.input(searchInput)
    wp.ele('xpath://div[@class="search-icon"]').click()
    wp.listen.start('web/v1/search/notes')
    #packet = wp.listen.wait()

    #Input search condition
    #On packet.response.body, find all links to images
    #re pattern: [{image_scene': 'WB_DFT', 'url': '(capture the link)'}
    pattern = "\[{'image_scene': 'WB_DFT', 'url': '(.{100,150})'}"
    #links = re.findall(pattern, str(packet.response.body))

    #check and open file to record saved images
    file = ''
    savedImages = []

    if not os.path.exists("./Images"):
        os.makedirs("./Images/")

    if os.path.isfile("links.txt"):
        with open('links.txt', 'r') as f:
            print("Reading links.txt into array")
            savedImages = set(f.readlines())
        f.close()
        file = open("links.txt", "a")
    else:
        file = open("links.txt", "w")

    sessionImages = []
    # imageCount = 50

    # Scrape until we reach our goal of imageCount
    while len(sessionImages) < imageCount:
        packet = wp.listen.wait()
        links = re.findall(pattern, str(packet.response.body))
        i = 0
        while i < len(links):
            if len(sessionImages) >= imageCount:
                break
            currLink = links[i]

            # save only images that we currently do not have
            if currLink not in savedImages:
                sessionImages.append(currLink)
                file.write(f"{links[i]}\n")
            i += 1
            print(i)
        ac.scroll(delta_y=3000)
        print("Scrolling down...")
        sleep(0.25)

    file.close()

    #Write images to ./Images
    for link in sessionImages:
        print("Saving image...")
        img_data = requests.get(link).content
        with open(f"./Images/{link[46:52]}.jpg", "wb") as handler:
            handler.write(img_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Demo script that requires exactly two inputs: topic and image count.",
        epilog=(
            "Examples:\n"
            "  python demo.py travel 10\n"
            "  python demo.py food 25"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    # two required *positional* arguments
    parser.add_argument("topic", help="Topic you want to scrape image from")
    parser.add_argument("count", help="Number of images to scrape", type=int)

    args = parser.parse_args()
    scrape(args.topic, args.count)

