from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
import os
import urllib.parse
import process

from dotenv import load_dotenv
load_dotenv()

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

## Flask アプリのインスタンス化
app = Flask(__name__)

## LINE のアクセストークン読み込み
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

## コールバックのおまじない
@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
	## APIインスタンス化
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## 返信
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text="Thank You!")]
	))

## オウム返しメッセージ
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
	## APIインスタンス化
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## 受信メッセージの中身を取得
	received_message = event.message.text

	## APIを呼んで送信者のプロフィール取得
	profile = line_bot_api.get_profile(event.source.user_id)
	display_name = profile.display_name

	## 返信メッセージ編集
	reply = f'{display_name}さんのメッセージ\n{received_message}'

	## オウム返し
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text=reply)]
	))

## PostbackActionに反応する
@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
	## APIインスタンス化
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## パース
	## event.postbackにURLパラメータ形式でデータが入っている(e.g. "action=buy&itemid=123")
	## 辞書型で取得する(e.g. data = {'action': 'buy', 'itemid': '123'})
	data = dict(urllib.parse.parse_qsl(event.postback.data))
	
	## 応答を生成
	messages = process.generate_reply(data)

	## 応答
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=messages
	))
