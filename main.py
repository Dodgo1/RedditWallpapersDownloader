import requests
import json
from pprint import pprint
import dotenv
from slugify import slugify
import os

dotenv.load_dotenv()
USERNAME = os.getenv("UNAME")
PASSWD = os.getenv("PASSWD")

secret = "Gxc-7tcn3j4tHnQHZoAR9Sdw3bCbMQ"
client_id = "AexKCSD9eaoyjk67LWdRPA"
auth = requests.auth.HTTPBasicAuth(client_id, secret)

reddit_url = "https://www.reddit.com/user/shagggYdOO/saved"

headers = {'User-Agent': 'Wallpapers/0.0.1'}

payload = {
    "grant_type": "password",
    'username': USERNAME,
    'password': PASSWD}

request = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=payload, headers=headers)
TOKEN = request.json()['access_token']

headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
dic = requests.get(f'https://oauth.reddit.com/user/{USERNAME}/saved?limit=100', headers=headers).json()
posts = dic['data']['children']
for post in posts:

    if post['data']['subreddit_name_prefixed'] == "r/wallpaper":
        title = str(post['data']['title']).replace(" ", "-")
        if 'is_gallery' in post['data']:
            for img_meta in post['data']['media_metadata']:
                url = f"https://i.redd.it/{img_meta}.jpg"
                file_name = slugify(f"{title}-{img_meta}")
                path = f"Wallpapers/{file_name}.png"
                img_data = requests.get(url).content
                with open(path, 'wb') as handler:
                    handler.write(img_data)
            continue

        path = f"Wallpapers/{slugify(title)}.png"
        url = post['data']['url_overridden_by_dest']
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
