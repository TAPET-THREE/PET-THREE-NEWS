import os
import re
import urllib.parse
import bs4
import feedparser
import requests
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexContainer,
    FlexMessage,
    MessagingApi,
    PushMessageRequest,
)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")


def get_og_image(url):
    """記事のURLからOGP画像（サムネイル画像）のURLを取得する"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=5)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
    except Exception:
        pass
    # サムネイルが見つからない場合のデフォルト画像（ペット関連画像）
    return "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=800"


def clean_title(title):
    """Google News RSSのタイトル末尾の出展メディア名を整形"""
    return re.sub(r" - [^-]+$", "", title)


def build_flex_message():
    """Google News RSSを取得し、LINEのFlex Message（カルーセル型）を生成する"""
    query = 'ペット -ペットボトル (ニュース OR 話題 OR 犬 OR 猫 OR 保護)'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"

    feed = feedparser.parse(rss_url)
    articles = feed.entries[:5]  # 最大5件を取得

    if not articles:
        return None

    bubbles = []

    for entry in articles:
        title = clean_title(entry.title)
        link = entry.link
        image_url = get_og_image(link)
        published = getattr(entry, "published", "")[:16]  # 日時（先頭部分）

        # Flex Message (1枚分のカード定義)
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                        "maxLines": 3,
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": published,
                                "size": "xs",
                                "color": "#aaaaaa",
                                "flex": 0,
                            }
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "記事を読む",
                            "uri": link,
                        },
                        "color": "#1DB446",
                    }
                ],
                "flex": 0,
            },
        }
        bubbles.append(bubble)

    # 複数カードを横スクロールできる「カルーセル」形式で構成
    flex_content = {"type": "carousel", "contents": bubbles}

    return FlexMessage(
        alt_text="🐾 本日のペットニュース",
        contents=FlexContainer.from_dict(flex_content),
    )


def send_line_message():
    flex_msg = build_flex_message()
    if not flex_msg:
        print("ニュース記事が見つかりませんでした。")
        return

    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        push_message_request = PushMessageRequest(
            to=LINE_USER_ID, messages=[flex_msg]
        )
        line_bot_api.push_message(push_message_request)


if __name__ == "__main__":
    send_line_message()


if __name__ == "__main__":
    news_text = get_pet_news()
    send_line_message(news_text)
