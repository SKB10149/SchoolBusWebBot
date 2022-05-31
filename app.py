from re import X
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, QuickReply
)
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials

## Flask ##
app = Flask(__name__)

## JSONリスト ##
# 学校名一覧JSON
flex_message_schooljson_dict = json.load(open("school.json","r",encoding="utf-8"))
# 登校JSON
flex_message_tokojson_dict = json.load(open("toko.json","r",encoding="utf-8"))
# 下校JSON
flex_message_gekojson_dict = json.load(open("toko.json","r",encoding="utf-8"))
# 備考JSON
flex_message_bikojson_dict = json.load(open("biko.json","r",encoding="utf-8"))

## LINE ##
line_bot_api = LineBotApi('LLaHIWKNBgwVlozdgSFtk3hYMa04AfYtEdGvXyYMIWZIIMUaZspah844LxKvxbARfEcKr0J8BeNi6jC47Eww4jbBu/lF43MgGJiwufZyL2XLP4J0bZXl+PDZVY5FOPg0kfQT4aYT3DZxj3fG3s/s/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d88565cbfef0134d3637555c856849de')

## Google Spread Sheet ##
# ※2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
credentials = ServiceAccountCredentials.from_json_keyfile_name("schoolbusserviceproject-8d96da3b9fb3.json", scope)
#OAuth2の資格情報を使用してGoogle APIにログイン。
gc = gspread.authorize(credentials)

SPREADSHEET_KEY = '1h1QcsQhISVUB8Zbj6mXfAdYYKTn1JHKzJVg-yueCO9M'\

# Connect test
@app.route("/")
def test():
    return "OK"

# Main App Program
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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

from time import time
users = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = event.source.user_id
    wb = gc.open_by_key(SPREADSHEET_KEY)
    ws = wb.worksheet('school Bus Uketsuke Sheet')
    
    # 乗車受付ボタン
    if event.message.text == "乗車受付":
        if not userId in users: #usersにuserIdがまだ入っていなければ真
            users[userId] = {}
        users[userId]["result"] = ""
        reply_message = "学校名を選択してください。"
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_message),
                FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_schooljson_dict
                )
            ]
        )
        users[userId]["mode"] = 0

    # 学校名
    elif users[userId]["mode"] == 0:
        ws = wb.worksheet('school Bus Uketsuke Sheet')
        if event.message.text == "羽村特別支援学校":
            flex_message_hamurajson_dict = json.load(open("hamura.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_hamurajson_dict
        elif event.message.text == "八王子西特別支援学校":
            flex_message_hachinishijson_dict = json.load(open("hachinishi.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_hachinishijson_dict
        elif event.message.text == "あきる野学園":
            flex_message_akirunojson_dict = json.load(open("akiruno.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_akirunojson_dict
        elif event.message.text == "七生特別支援学校":
            flex_message_nanaojson_dict = json.load(open("nanao.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_nanaojson_dict
        elif event.message.text == "青峰学園":
            flex_message_seihojson_dict = json.load(open("seiho.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_seihojson_dict
        elif event.message.text == "八王子盲学校":
            flex_message_hachimojson_dict = json.load(open("hachimo.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_hachimojson_dict
        elif event.message.text == "村山特別支援学校":
            flex_message_murayamajson_dict = json.load(open("murayama.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_murayamajson_dict
        elif event.message.text == "武蔵台学園":
            flex_message_musashidaijson_dict = json.load(open("musashidai.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_musashidaijson_dict
        elif event.message.text == "田無特別支援学校":
            flex_message_tanashijson_dict = json.load(open("tanashi.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_tanashijson_dict
        elif event.message.text == "清瀬特別支援学校":
            flex_message_kiyosejson_dict = json.load(open("kiyose.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_kiyosejson_dict
        elif event.message.text == "立川学園":
            flex_message_tachikawajson_dict = json.load(open("tachikawa.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_tachikawajson_dict
        elif event.message.text == "小金井特別支援学校":
            flex_message_koganeijson_dict = json.load(open("koganei.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_koganeijson_dict
        elif event.message.text == "光明学園":
            flex_message_komeijson_dict = json.load(open("komei.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_komeijson_dict
        elif event.message.text == "小平特別支援学校":
            flex_message_kodairajson_dict = json.load(open("kodaira.json","r",encoding="utf-8"))
            flex_message_json_dict = flex_message_kodairajson_dict
        else:
            reply_message = f"{event.message.text} は、弊社では受け付けておりません。"
            repMessage(event, reply_message)
            users[userId]["mode"] = 0
            exit()
        
        users[userId]["school"] = event.message.text
        ws.update.cell(2,4,event.message.text)
        users[userId]["result"] += users[userId]["school"]
        reply_message = f"{users[userId]['result']}"
        reply_message2 = "コース名を選択してください。"
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_message),
                TextSendMessage(text=reply_message2),
                FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_json_dict
                )
            ]
        )
        users[userId]["mode"] = 1

    # コース名
    elif users[userId]["mode"] == 1: 
        users[userId]["cource"] = event.message.text
        users[userId]["result"] += "、" + users[userId]["cource"] + "コース"
        reply_message = f"{users[userId]['result']} が入力されました。"
        reply_message2 = "氏名(ひらがな or カタカナ)を入力してください。"
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_message),
                TextSendMessage(text=reply_message2), #氏名
            ]
        )
        users[userId]["mode"] = 2

    # 氏名
    elif users[userId]["mode"] == 2:
        if event.message.text != "":
            users[userId]["shimei"] = event.message.text
            users[userId]["result"] += "、" + users[userId]["shimei"] + "さん"
            reply_message = f"{users[userId]['result']} "
            reply_message2 = "いつから？(例:2022年5月1日 2022/5/1)"
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=reply_message),
                    TextSendMessage(text=reply_message2),
                ]
            )
            users[userId]["mode"] = 3

    # いつから
    elif users[userId]["mode"] == 3:
        if event.message.text != "":
            users[userId]["dateFrom"] = event.message.text
            users[userId]["result"] += "、" + users[userId]["dateFrom"] + " ～ "
            reply_message = f"{users[userId]['result']} "
            reply_message2 = "いつまで？(例:2022年5月1日 2022/5/1)"
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=reply_message),
                    TextSendMessage(text=reply_message2),
                ]
            )
            users[userId]["mode"] = 4

    # いつまで
    elif users[userId]["mode"] == 4:
        if event.message.text != "":
            users[userId]["dateTo"] = event.message.text
            users[userId]["result"] += users[userId]["dateTo"]
            reply_message = f"{users[userId]['result']} "
            reply_message2 = "登校便の乗車について"
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=reply_message),
                    TextSendMessage(text=reply_message2),
                    FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_tokojson_dict
            )
                ]
            )
            users[userId]["mode"] = 5

    # 登校乗る、乗らない、または空白
    elif users[userId]["mode"] == 5:
        users[userId]["toko"] = event.message.text

        if event.message.text != "休む":
            users[userId]["result"] += "\n登校便：　" + users[userId]["toko"]
        else:
            users[userId]["result"] += users[userId]["toko"]

        reply_message = f"{users[userId]['result']} "
        
        if event.message.text == "休む":
            reply_message2 = "特記事項があれば入力してください。"
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=reply_message),
                    TextSendMessage(text=reply_message2),
                ]
            )
            users[userId]["mode"] = 7
        else:
            reply_message2 = "下校便の乗車について"
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=reply_message),
                    TextSendMessage(text=reply_message2),
                    FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_gekojson_dict
            )
                ]
            )
            users[userId]["mode"] = 6

    # 下校乗る、乗らない、または空白
    elif users[userId]["mode"] == 6:
        users[userId]["geko"] = event.message.text
        users[userId]["result"] += users[userId]["geko"]
        reply_message = f"{users[userId]['result']} "
        reply_message2 = "特記事項があれば入力してください。"
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_message),
                TextSendMessage(text=reply_message2),
                FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_bikojson_dict
                )
            ]
        )
        users[userId]["mode"] = 7

    # 備考
    elif users[userId]["mode"] == 7:
        users[userId]["biko"] = event.message.text
        users[userId]["result"] += "\n特記事項「 " + users[userId]["biko"] + " 」"
        reply_message = f"{users[userId]['result']} "
        reply_message2 = "乗車連絡を受け付けました。\nご連絡ありがとうございました。"
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=reply_message),
                TextSendMessage(text=reply_message2),
            ]
        )
        users[userId]["mode"] = 0

    # 裏コマンド（ネタ）
    elif event.message.text == "ぬるぽ":
        if not userId in users: #usersにuserIdがまだ入っていなければ真
            users[userId] = {}
        reply_message = "ｶﾞｯ"
        users[userId]["mode"] = 0
        repMessage(event, reply_message)

# LINEへメッセージを送信する処理関数
def repMessage(event, reply_message):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))

if __name__ == "__main__":
    app.run()