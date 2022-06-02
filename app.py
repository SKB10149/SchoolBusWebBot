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
import logging

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from time import time
from datetime import date, datetime

#from flask_moment import Moment

users = {}
worksheets = {} #辞書を初期化する
separator = "==================="

## Flask ##
app = Flask(__name__)

## LINE ##
line_bot_api = LineBotApi('LLaHIWKNBgwVlozdgSFtk3hYMa04AfYtEdGvXyYMIWZIIMUaZspah844LxKvxbARfEcKr0J8BeNi6jC47Eww4jbBu/lF43MgGJiwufZyL2XLP4J0bZXl+PDZVY5FOPg0kfQT4aYT3DZxj3fG3s/s/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d88565cbfef0134d3637555c856849de')

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = event.source.user_id
    cources = ["旧青梅","友愛","成木","東大和","羽村","武蔵村山","御岳","奥多摩","青梅","立川","新青梅街道","福生","立川諏訪","青梅橋","昭和公園","江戸街道","多摩川","モノレール","国立","立川南","西東京","小平","富士見町","東村山","陣馬","石川","川口","大和田","東中神","檜原","昭島","新五日市","拝島","武蔵増戸","急行檜原","日野駅","万願寺","二俣尾","西","西砂","こぶし","仙川"]

    if event.message.text[12:] == "スクールバス乗車電話受付":
        print("hoge")

    # 乗車受付ボタン押下
    elif event.message.text == "乗車受付":
        if not userId in users: #usersにuserIdがまだ入っていなければ真
            users[userId] = {}

        # 結果を初期化
        users[userId]["result"] = ""

        reply_message = "学校名を選択してください。"

        # 学校名一覧JSON
        flex_message_schooljson_dict = json.load(open("school.json","r",encoding="utf-8"))
        
        # LINEで表示
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

    # 学校名押下
    elif event.message.text[-2:] == "学校":
        selectSchool(event, event.message.text)
    elif event.message.text[-2:] == "学園":
        selectSchool(event, event.message.text)

    # コース名押下
    elif event.message.text in cources:
        selectCource(event, event.message.text)

    # 氏名入力時
    elif event.message.text not in cources:
        studentName(event,event.message.text)
    
    # いつから？
    elif event.message.text == "いつから？":
        # ex:20220601 -> 2022/06/01に変換して格納する
        # 桁数は8桁とする
        dateFrom(event, event.message.text)
    # いつまで？
    elif event.message.text == "いつまで？":
        # ex:20220601 -> 2022/06/01
        # 桁数は8桁とする
        dateTo(event, event.message.text)

    # # コース名
    # elif event.message.text:
    #     selectCource():
    # elif users[userId]["mode"] == 1:
    #     # 選択されたコース名を格納
    #     users[userId]["cource"] = event.message.text
    #     # 結果へ書き込み
    #     users[userId]["result"] += "、" + users[userId]["cource"] + "コース"

    #     reply_message = "氏名(ひらがな or カタカナ)を入力してください。"
    #     # LINEで表示
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [
    #             TextSendMessage(text=reply_message)
    #         ]
    #     )
    #     users[userId]["mode"] = 2
    #     repMessage(event, event.message.text)
    #     logging.debug()

    # # 氏名
    # elif users[userId]["mode"] == 2:
    #     if event.message.text != "":
    #         users[userId]["shimei"] = event.message.text
    #         users[userId]["result"] += "、" + users[userId]["shimei"] + "さん"

    #         reply_message = "いつから？(例:2022年5月1日 2022/5/1)"
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text=reply_message)
    #             ]
    #         )
    #         users[userId]["mode"] = 3

    # # いつから
    # elif users[userId]["mode"] == 3:
    #     if event.message.text != "":
    #         users[userId]["dateFrom"] = event.message.text
    #         users[userId]["result"] += "、" + users[userId]["dateFrom"] + " ～ "
            
    #         reply_message = "いつまで？(例:2022年5月1日 2022/5/1)"
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text=reply_message)
    #             ]
    #         )
    #         users[userId]["mode"] = 4

    # # いつまで
    # elif users[userId]["mode"] == 4:
    #     if event.message.text != "":
    #         users[userId]["dateTo"] = event.message.text
    #         users[userId]["result"] += users[userId]["dateTo"]
            
    #         reply_message = "登校便の乗車について"
    #         # 登校JSON
    #         flex_message_tokojson_dict = json.load(open("toko.json","r",encoding="utf-8"))
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text=reply_message),
    #                 FlexSendMessage(
    #                     alt_text="alt_text",
    #                     contents=flex_message_tokojson_dict
    #                 )
    #             ]
    #         )
    #         users[userId]["mode"] = 5

    # # 登校乗る、乗らない、休む
    # elif users[userId]["mode"] == 5:
    #     users[userId]["toko"] = event.message.text

    #     if event.message.text != "休む":
    #         users[userId]["result"] += "\n登校便: " + users[userId]["toko"]
    #     else:
    #         users[userId]["result"] += users[userId]["toko"]
        
    #     if event.message.text == "休む":
    #         reply_message = "特記事項があれば入力してください。"
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text=reply_message)
    #             ]
    #         )
    #         users[userId]["mode"] = 7
    #     else:
    #         reply_message = "下校便の乗車について"
    #         # 下校JSON
    #         flex_message_gekojson_dict = json.load(open("toko.json","r",encoding="utf-8"))
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text=reply_message),
    #                 FlexSendMessage(
    #                     alt_text="alt_text",
    #                     contents=flex_message_gekojson_dict
    #                 )
    #             ]
    #         )
    #         users[userId]["mode"] = 6

    # # 下校乗る、乗らない、または空白
    # elif users[userId]["mode"] == 6:
    #     users[userId]["geko"] = event.message.text
    #     users[userId]["result"] += users[userId]["geko"]
        
    #     reply_message = "特記事項があれば入力してください。"
    #     # 備考JSON
    #     flex_message_bikojson_dict = json.load(open("biko.json","r",encoding="utf-8"))
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [
    #             TextSendMessage(text=reply_message),
    #             FlexSendMessage(
    #                 alt_text="alt_text",
    #                 contents=flex_message_bikojson_dict
    #             )
    #         ]
    #     )
    #     users[userId]["mode"] = 7

    # # 備考
    # elif users[userId]["mode"] == 7:
    #     users[userId]["biko"] = event.message.text
    #     users[userId]["result"] += "\n特記事項「 " + users[userId]["biko"] + " 」"
    #     reply_message = f"{users[userId]['result']} "
    #     reply_message2 = "乗車連絡を受け付けました。\nご連絡ありがとうございました。"
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [
    #             TextSendMessage(text=reply_message),
    #             TextSendMessage(text=reply_message2),
    #         ]
    #     )
    #     users[userId]["mode"] = 0

    # 裏コマンド（ネタ）
    elif event.message.text == "ぬるぽ":
        if not userId in users: #usersにuserIdがまだ入っていなければ真
            users[userId] = {}
        reply_message = "ｶﾞｯ"
        users[userId]["mode"] = 0
        repMessage(event, reply_message)

# 学校名が選択されたときの動作
def selectSchool(event, strSchool):
    if strSchool == "羽村特別支援学校":
        flex_message_hamurajson_dict = json.load(open("hamura.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_hamurajson_dict
    elif strSchool == "八王子西特別支援学校":
        flex_message_hachinishijson_dict = json.load(open("hachinishi.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_hachinishijson_dict
    elif strSchool == "あきる野学園":
        flex_message_akirunojson_dict = json.load(open("akiruno.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_akirunojson_dict
    elif strSchool == "七生特別支援学校":
        flex_message_nanaojson_dict = json.load(open("nanao.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_nanaojson_dict
    elif strSchool == "青峰学園":
        flex_message_seihojson_dict = json.load(open("seiho.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_seihojson_dict
    elif strSchool == "八王子盲学校":
        flex_message_hachimojson_dict = json.load(open("hachimo.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_hachimojson_dict
    elif strSchool == "村山特別支援学校":
        flex_message_murayamajson_dict = json.load(open("murayama.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_murayamajson_dict
    elif strSchool == "武蔵台学園":
        flex_message_musashidaijson_dict = json.load(open("musashidai.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_musashidaijson_dict
    elif strSchool == "田無特別支援学校":
        flex_message_tanashijson_dict = json.load(open("tanashi.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_tanashijson_dict
    elif strSchool == "清瀬特別支援学校":
        flex_message_kiyosejson_dict = json.load(open("kiyose.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_kiyosejson_dict
    elif strSchool == "立川学園":
        flex_message_tachikawajson_dict = json.load(open("tachikawa.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_tachikawajson_dict
    elif strSchool == "小金井特別支援学校":
        flex_message_koganeijson_dict = json.load(open("koganei.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_koganeijson_dict
    elif strSchool == "光明学園":
        flex_message_komeijson_dict = json.load(open("komei.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_komeijson_dict
    elif strSchool == "小平特別支援学校":
        flex_message_kodairajson_dict = json.load(open("kodaira.json","r",encoding="utf-8"))
        flex_message_json_dict = flex_message_kodairajson_dict
    else:
        reply_message = f"{strSchool} は、弊社では受け付けておりません。"
        repMessage(event, reply_message)
        exit()

    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=strSchool),
            FlexSendMessage(
                alt_text="alt_text",
                contents=flex_message_json_dict
            )
        ]
    )

# コース名が選択された時の動作
def selectCource(event, strCource):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=strCource+"コース"),
            TextSendMessage(text="氏名を入力して下さい（ひらがな or カタカナ）")
        ]
    )

# 氏名の入力時の動作
def studentName(event,strName):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=strName+"さん"),
            TextSendMessage(text="いつから？")
        ]
    )

# いつから？
def dateFrom(event,dateFrom_):
    tempFrom = datetime.strptime(dateFrom_, "%Y/%m/%d").date()
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=tempFrom+" ～ "),
            TextSendMessage(text="いつまで？")
        ]
    )

# いつまで？
def dateTo(event,dateTo_):
    tempTo = datetime.strptime(dateTo_, "%Y/%m/%d").date()
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=tempTo),
            #FlexMessage登校便乗る？休み
        ]
    )

# 登校便に乗る？休み？
def rideTokobin(event,toko):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="工事中"),
            #FlexMessage下校便乗る？休み
        ]
    )
# 下校便に乗る？
def rideGekobin(event,geko):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="工事中"),
            #FlexMessage特記事項
        ]
    )
    
# 特記事項
def spMessage(event,biko):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="工事中")
        ]
    )

# LINEへメッセージを送信する処理関数
def repMessage(event, reply_message):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))



# @handler.add(FollowEvent)
# @handler.add(UnfollowEvent)

if __name__ == "__main__":
    app.run()