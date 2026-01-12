import os
import re
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# ---------------- VK ----------------
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_API = "https://api.vk.com/method"
VK_VERSION = "5.199"


def get_vk_views(url):
    post = re.search(r"wall(-?\d+)_(\d+)", url)
    video = re.search(r"video(-?\d+)_(\d+)", url)

    if post:
        owner, post_id = post.group(1), post.group(2)
        r = requests.get(f"{VK_API}/wall.getById", params={
            "posts": f"{owner}_{post_id}",
            "access_token": VK_TOKEN,
            "v": VK_VERSION
        }).json()
        try:
            return r["response"][0]["views"]["count"]
        except:
            return "❌ VK не вернул просмотры"

    if video:
        owner, vid = video.group(1), video.group(2)
        r = requests.get(f"{VK_API}/video.get", params={
            "videos": f"{owner}_{vid}",
            "access_token": VK_TOKEN,
            "v": VK_VERSION
        }).json()
        try:
            return r["response"]["items"][0]["views"]
        except:
            return "❌ VK не вернул просмотры"

    return None


# ---------------- OK ----------------
def get_ok_views(url):
    try:
        r = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
        views = re.search(r'"count":(\d+),"className":"views"', r.text)
        if views:
            return int(views.group(1))
        return "❌ Не удалось найти просмотры в OK"
    except:
        return "❌ Ошибка доступа к OK"


# ---------------- ДЗЕН ----------------
def get_zen_views(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        match = re.search(r'"viewCount":(\d+)', r.text)
        if match:
            return int(match.group(1))
        return "❌ Дзен не дал просмотры"
    except:
        return "❌ Ошибка доступа к Дзен"


@app.route("/", methods=["GET", "POST"])
def index():
    views = None
    error = None

    if request.method == "POST":
        url = request.form["url"].strip()

        if "vk.com" in url:
            views = get_vk_views(url)

        elif "ok.ru" in url:
            views = get_ok_views(url)

        elif "zen.yandex" in url:
            views = get_zen_views(url)

        else:
            error = "Платформа не распознана"

    return render_template("index.html", views=views, error=error)


if __name__ == "__main__":
    app.run()
