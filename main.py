import os
import urllib.parse
import feedparser
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)

# 1. 環境変数からトークンとユーザーIDを取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")


def get_pet_news():
    # Google News RSSから「ペット ニュース」の最新情報を取得
    keyword = "ペット"
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja"

    feed = feedparser.parse(rss_url)

    # 上位3件を抽出
    articles = feed.entries[:3]
    if not articles:
        return "本日のペット関連ニュースはありません。"

    message_text = "🐾 本日のペットニュース 🐾\n\n"
    for i, entry in enumerate(articles, 1):
        message_text += f"{i}. {entry.title}\n{entry.link}\n\n"

    return message_text.strip()


def send_line_message(text):
    # LINE Messaging APIを使ってプッシュメッセージを送信
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        push_message_request = PushMessageRequest(
            to=LINE_USER_ID, messages=[TextMessage(text=text)]
        )
        line_bot_api.push_message(push_message_request)


if __name__ == "__main__":
    news_text = get_pet_news()
    send_line_message(news_text)
