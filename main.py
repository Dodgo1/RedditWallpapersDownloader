import requests
import dotenv
from slugify import slugify
import os
import hashlib
from PIL import Image

dotenv.load_dotenv()
USERNAME = os.getenv("UNAME")
PASSWD = os.getenv("PASSWD")
CLIENT_ID = os.getenv("CLIENT_ID")
SECRET = os.getenv("SECRET")
APP_NAME = os.getenv("APP_NAME")
APP_VERSION = os.getenv("APP_VERSION")
RESOLUTION = os.getenv("RESOLUTION")

download_folder = "wallpapers"
search_limit = 100

if not os.path.isdir(download_folder):
    os.mkdir(download_folder)

reddit_url = f"https://www.reddit.com/user/{USERNAME}/saved"
headers = {f'User-Agent': f'{APP_NAME}/{APP_VERSION}'}
payload = {
    "grant_type": "password",
    'username': USERNAME,
    'password': PASSWD}

TOKEN = requests.post('https://www.reddit.com/api/v1/access_token',
                      auth=(CLIENT_ID, SECRET),
                      data=payload,
                      headers=headers).json()['access_token']

headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
dic = requests.get(f'https://oauth.reddit.com/user/{USERNAME}/saved?limit={search_limit}', headers=headers).json()
posts = dic['data']['children']

for post in posts:  # iterate over posts

    if post['data']['subreddit_name_prefixed'] != "r/wallpaper":  # skip posts out of r/wallpaper
        continue

    img_title = slugify(post['data']['title'])

    # handle reddits gallery scenario
    if 'is_gallery' in post['data']:

        for img_meta in post['data']['media_metadata']:
            url = f"https://i.redd.it/{img_meta}.jpg"
            file_name = f"{img_title}-{slugify(img_meta)}.png"
            path = f"{download_folder}/{file_name}"
            img_new_data = requests.get(url).content

            try:  # write file, if same exists, compare contents and overwrite with new if different
                with open(path, 'xb') as file_handler:
                    file_handler.write(img_new_data)
                    print("🤯 New file added - gallery scenario")
            except FileExistsError:
                print("🥵File already exists")
                with open(path, 'w+b') as existing_file:
                    exist_hash = hashlib.sha1(existing_file.read()).hexdigest()
                    new_hash = hashlib.sha1(img_new_data).hexdigest()
                    if exist_hash == new_hash:
                        print("🧠Same hashes")
                        continue
                    print("🥶Different hashes - updating img")
                    existing_file.seek(0)
                    existing_file.write(img_new_data)
                    existing_file.truncate()
        continue

    # handle no gallery scenario
    path = f"{download_folder}/{img_title}.png"
    url = post['data']['url_overridden_by_dest']
    img_new_data = requests.get(url).content
    with open(path, 'xb') as handler:
        handler.write(img_new_data)
    print("🤯 New file added")

# resize all images in the folder to given resolution
print("‍✈️Resizing all images")

files = os.listdir(download_folder)
size = int(RESOLUTION.split("x")[0]), int(RESOLUTION.split("x")[1])

for file in files:
    with Image.open(f"{download_folder}/{file}") as image:
        if (image.width, image.height) == size:
            print("☠️Correct image size")
            continue

        new_img = image.resize(size)
        os.remove(file)
        new_img.save(file)  # TODO: change size in file name (regex)

        print("🪒 Resized an image")
