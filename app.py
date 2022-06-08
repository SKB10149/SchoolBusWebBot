from re import X
import re
from webbrowser import get
from flask import Flask, render_template, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, PostbackTemplateAction, PostbackEvent, FollowEvent, UnfollowEvent
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
    return "Hello Flask in Python"

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
    text = event.message.text
    userId = event.source.user_id
    cources = ["旧青梅","友愛","成木","東大和","羽村","武蔵村山","御岳","奥多摩","青梅","立川","新青梅街道","福生","立川諏訪","青梅橋","昭和公園","江戸街道","多摩川","モノレール","国立","立川南","西東京","小平","富士見町","東村山","陣馬","石川","川口","大和田","東中神","檜原","昭島","新五日市","拝島","武蔵増戸","急行檜原","日野駅","万願寺","二俣尾","西","西砂","こぶし","仙川"]
    
    MySession.register(userId)
    
    if ((MySession.read_context(userId) == "1" or 
        MySession.read_context(userId) == "2" )):
        line_bot_api.reply_message(
            event.reply_token,
            [   
                TextSendMessage(text="初めにログインしてください。")
            ]
        )
        # 現在のstatusを消して新規statusで初期化。
        MySession.reset(userId)
    
    elif text == "キャンセル":
        line_bot_api.reply_message(
            event.reply_token,
            [   
                TextSendMessage(text="キャンセルされました。")
            ]
        )
        # 現在のstatusを消して新規statusで初期化。
        MySession.reset(userId)

    elif text[:12] == "スクールバス乗車電話受付":
        # LINEで表示
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text="以下の連絡先へお願いします。"),
                TextSendMessage(text="042-579-7644")
            ]
        )
        # 現在のstatusを消して新規statusで初期化。
        MySession.reset(userId)

    # 裏コマンド（ネタ）
    elif text == "ぬるぽ":
        reply_message = "ｶﾞｯ"
        repMessage(event, reply_message)
        # 現在のstatusを消して新規statusで初期化。
        MySession.reset(userId)

    elif MySession.read_context(userId) == "0":
        if text == "ログイン":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("ログインに成功しました。/n乗車受付ボタンをタップしてください。")
            )
            MySession.update_context(userId, "1")
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("はじめに「ログイン」ボタンをタップしてログインしてください。")
            )

    # 乗車受付ボタン押下
    elif MySession.read_context(userId) == "1":
        if event.message.text == "乗車受付":
            MySession.update_context(userId, "2")
            MySession.update_uketsuketype(userId, "乗車受付")

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
        else:
            error(event, userId)

    # 学校名押下
    elif MySession.read_context(userId) == "2":
        if text[-2:] == "学校":
            MySession.update_context(userId, "3")
            flex_message_json_dict = selectSchool(event, text)
            if flex_message_json_dict == 0:
                error(event, userId)
            else:
                MySession.update_gakko(userId, "text")
        elif text[-2:] == "学園":
            MySession.update_context(userId, "3")
            flex_message_json_dict = selectSchool(event, text)
            if flex_message_json_dict == 0:
                error(event, userId)
            else:
                MySession.update_gakko(userId, "text")
        else:
            error(event, userId)

        # LINEで表示
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=text),
                FlexSendMessage(
                    alt_text="alt_text",
                    contents=flex_message_json_dict
                )
            ]
        )

    # コース名押下
    elif MySession.read_context(userId) == "3":
        if text in cources:
            MySession.update_context(userId, "4")
            strCource = selectCource(event, text)
            MySession.update_cource(userId, strCource)

            # LINEで表示
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=strCource+"コース"),
                    TextSendMessage(text="氏名を入力して下さい（ひらがな or カタカナ）")
                ]
            )
        else:
            error(event, userId)

    # 氏名入力
    elif MySession.read_context(userId) == "4":
        MySession.update_context(userId, "5")
        strName = studentName(event,text)
        MySession.update_shimei(userId, strName)  

        # LINEで表示
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=strName+"さん")
            ]
        )  

    # いつから～いつまで
    elif MySession.read_context(userId) == "5":
        if text == "期間":
            MySession.update_context(userId,"6")
            flex_message_json_dict = json.load(open("dateFromTo.json","r",encoding="utf-8"))

            # LINEで表示
            line_bot_api.reply_message(
                event.reply_token,
                [
                    FlexSendMessage(
                        alt_text="alt_text",
                        contents=flex_message_json_dict
                    )
                ]
            )
        elif text == "キャンセル":
            error(event, userId)
        else:
            repMessage(event, "期間ボタンを押下してください。")
    
    # 登下校乗る乗らない　か　休み
    elif MySession.read_context(userId) == "6":
        if text == "登下校":
            MySession.update_context(userId,"7")
            flex_message_json_dict = json.load(open("togeko.json","r",encoding="utf-8"))

            # LINEで表示
            line_bot_api.reply_message(
                event.reply_token,
                [
                    FlexSendMessage(
                        alt_text="alt_text",
                        contents=flex_message_json_dict
                    )
                ]
            )

        elif text == "キャンセル":
            error(event, userId)
        else:
            repMessage(event, "期間を指定して下さい。/n次に進む場合は、登下校ボタンをタップしてください。")

    elif MySession.read_context(userId) == "7":
        if text == "登校：乗る":
            MySession.update_toko(userId, text)
        elif text == "登校：乗らない":
            MySession.update_toko(userId, text)
        elif text == "下校：乗る":
            MySession.update_geko(userId, text)
        elif text == "下校：乗らない":
            MySession.update_geko(userId, text)
        elif text == "休み":
            MySession.update_sonota(userId, text)

        # 備考
        if text == "備考":
            MySession.update_context(userId,"8")
            flex_message_json_dict = json.load(open("biko.json","r",encoding="utf-8"))
            # LINEで表示
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text="特記事項がある場合は入力してください。/nない場合は「なし」をタップしてください。"),
                    FlexSendMessage(
                        alt_text="alt_text",
                        contents=flex_message_json_dict
                    )
                ]
            )

    # 受付完了
    elif MySession.read_context(userId) == "8":
        repMessage(event, "乗車連絡を受付ました。/nご連絡ありがとうございました。")
        MySession.update_context(userId, "0")

# ポストバックイベント(dateTimePicker)
@handler.add(PostbackEvent)
def on_postback(event):
    userId = event.source.user_id
    postback_msg = event.postback.data
    
    if postback_msg == "datefrom":
        line_bot_api.push_message(
            to=userId,
            messages=TextSendMessage(text=event.postback.params['date'].replace('-','/'))
        )
    elif postback_msg == "dateto":
        line_bot_api.push_message(
            to=userId,
            messages=TextSendMessage(text=event.postback.params['date'].replace('-','/'))
        )
    elif  postback_msg == "cancel":
        error(event, userId)

@handler.add(FollowEvent)
def on_followevent(event):
    print("hogehoge")

@handler.add(UnfollowEvent)
def on_unfollowevent(event):
    print("hogehoge")

# Class
class Status:
    def __init__(self):
        self.context = "0"
        self.uketsuketype = ""
        self.gakko = ""
        self.cource = ""
        self.shimei = ""
        self.dateFrom = ""
        self.dateTo = ""
        self.toko = ""
        self.geko = ""
        self.sonota = ""
        self.biko = ""
    def get_context(self):
        return self.context
    def set_context(self, context):
        self.context = context
    def get_uketsuketype(self):
        return self.uketsuketype
    def set_uketsuketype(self, uketsuketype):
        self.uketsuketype = uketsuketype
    def get_gakko(self):
        return self.gakko
    def set_gakko(self, gakko):
        self.gakko = gakko
    def get_cource(self):
        return self.cource
    def set_cource(self, cource):
        self.cource = cource
    def get_shimei(self):
        return self.shimei
    def set_shimei(self, shimei):
        self.shimei = shimei
    def get_dateFrom(self):
        return self.dateFrom
    def set_dateFrom(self, dateFrom):
        self.dateFrom = dateFrom
    def get_dateTo(self):
        return self.dateTo
    def set_dateTo(self, dateTo):
        self.dateTo = dateTo
    def get_toko(self):
        return self.toko
    def set_toko(self, toko):
        self.toko = toko
    def get_geko(self):
        return self.geko
    def set_geko(self, geko):
        self.geko = geko
    def get_sonota(self):
        return self.sonota
    def set_sonota(self, sonota):
        self.sonota = sonota
    def get_biko(self):
        return self.biko
    def set_biko(self, biko):
        self.biko = biko

class MySession:
    _status_map = dict()
    def register(user_id):
        if MySession._get_status(user_id) is None:
            MySession._put_status(user_id, Status())

    def reset(user_id):
        MySession._put_status(user_id, Status())

    def _get_status(user_id):
        return MySession._status_map.get(user_id)

    def _put_status(user_id, status: Status):
        MySession._status_map[user_id]= status

    def read_context(user_id):
        return MySession._status_map.get(user_id).get_context()
    def read_uketsuketype(user_id):
        return MySession._status_map.get(user_id).get_uketsuketype()
    def read_gakko(user_id):
        return MySession._status_map.get(user_id).get_gakko()
    def read_cource(user_id):
        return MySession._status_map.get(user_id).get_cource()
    def read_shimei(user_id):
        return MySession._status_map.get(user_id).get_shimei()
    def read_dateFrom(user_id):
        return MySession._status_map.get(user_id).get_dateFrom()
    def read_dateTo(user_id):
        return MySession._status_map.get(user_id).get_dateTo()
    def read_toko(user_id):
        return MySession._status_map.get(user_id).get_toko()
    def read_geko(user_id):
        return MySession._status_map.get(user_id).get_geko()
    def read_sonota(user_id):
        return MySession._status_map.get(user_id).get_sonota()
    def read_biko(user_id):
        return MySession._status_map.get(user_id).get_biko()

    def update_context(user_id, context):
        new_status = MySession._status_map.get(user_id)
        new_status.set_context(context)
        MySession._status_map[user_id] = new_status
    def update_uketsuketype(user_id, uketsuketype):
        new_status = MySession._status_map.get(user_id)
        new_status.set_uketsuketype(uketsuketype)
        MySession._status_map[user_id] = new_status
    def update_gakko(user_id, gakko):
        new_status = MySession._status_map.get(user_id)
        new_status.set_gakko(gakko)
        MySession._status_map[user_id] = new_status
    def update_cource(user_id, cource):
        new_status = MySession._status_map.get(user_id)
        new_status.set_cource(cource)
        MySession._status_map[user_id] = new_status
    def update_shimei(user_id, shimei):
        new_status = MySession._status_map.get(user_id)
        new_status.set_shimei(shimei)
        MySession._status_map[user_id] = new_status
    def update_dateFrom(user_id, dateFrom):
        new_status = MySession._status_map.get(user_id)
        new_status.set_dateFrom(dateFrom)
        MySession._status_map[user_id] = new_status
    def update_dateTo(user_id, dateTo):
        new_status = MySession._status_map.get(user_id)
        new_status.set_dateTo(dateTo)
        MySession._status_map[user_id] = new_status
    def update_toko(user_id, toko):
        new_status = MySession._status_map.get(user_id)
        new_status.set_toko(toko)
        MySession._status_map[user_id] = new_status
    def update_geko(user_id, geko):
        new_status = MySession._status_map.get(user_id)
        new_status.set_geko(geko)
        MySession._status_map[user_id] = new_status
    def update_sonota(user_id, sonota):
        new_status = MySession._status_map.get(user_id)
        new_status.set_sonota(sonota)
        MySession._status_map[user_id] = new_status
    def update_biko(user_id, biko):
        new_status = MySession._status_map.get(user_id)
        new_status.set_biko(biko)
        MySession._status_map[user_id] = new_status

## 関数 ##
# 学校名が選択されたときの動作 & コースFlex起動
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
        return 0

    return flex_message_json_dict

# コース名が選択された時の動作
def selectCource(event, strCource):
    return strCource

# 氏名の入力時の動作
def studentName(event,strName):
    return strName
    
# いつから？ & いつまでdateTimePicker起動
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

# いつまで？ & 登校便Flex起動
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

# 登校便に乗る？休み？ & 下校便Flex起動
def rideTokobin(event,toko):
    # LINEで表示
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="工事中"),
            #FlexMessage下校便乗る？休み
        ]
    )
# 下校便に乗る？ & 特記事項Flex起動
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

# LINEへ単一メッセージを送信する関数
def repMessage(event, reply_message):
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))

# エラー
def error(event, userId):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage("最初からやり直します。"),
    )
    # 現在のstatusを消して新規statusで初期化。
    MySession.reset(userId)
    exit()

## アプリケーション実行 ##
if __name__ == "__main__":
    app.run()