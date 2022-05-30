from re import X
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
)
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials

## Flask ##
app = Flask(__name__)

## JSONリスト ##
# 学校名一覧JSON
flex_message_schooljson_dict = json.load(open("school.json","r",encoding="utf-8"))
# コース名一覧JSON
flex_message_akirunojson_dict = json.load(open("akiruno.json","r",encoding="utf-8"))
flex_message_hachimojson_dict = json.load(open("hachimo.json","r",encoding="utf-8"))
flex_message_hachinishijson_dict = json.load(open("hachinishi.json","r",encoding="utf-8"))
flex_message_hamurajson_dict = json.load(open("hamura.json","r",encoding="utf-8"))
flex_message_kiyosejson_dict = json.load(open("kiyose.json","r",encoding="utf-8"))
flex_message_kodairajson_dict = json.load(open("kodaira.json","r",encoding="utf-8"))
flex_message_koganeijson_dict = json.load(open("koganei.json","r",encoding="utf-8"))
flex_message_komeijson_dict = json.load(open("komei.json","r",encoding="utf-8"))
flex_message_murayamajson_dict = json.load(open("murayama.json","r",encoding="utf-8"))
flex_message_musashidaijson_dict = json.load(open("musashidai.json","r",encoding="utf-8"))
flex_message_nanaojson_dict = json.load(open("nanao.json","r",encoding="utf-8"))
flex_message_seihojson_dict = json.load(open("seiho.json","r",encoding="utf-8"))
flex_message_tachikawajson_dict = json.load(open("tachikawa.json","r",encoding="utf-8"))
flex_message_tanashijson_dict = json.load(open("tanashi.json","r",encoding="utf-8"))
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

# ①「名前」で取得
# wb = gc.open('schoolbus')
# print(wb)
# ②「キー」で取得
SPREADSHEET_KEY = '1h1QcsQhISVUB8Zbj6mXfAdYYKTn1JHKzJVg-yueCO9M'
wb = gc.open_by_key(SPREADSHEET_KEY)
print(wb)
# ③「URL」で取得
# SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1h1QcsQhISVUB8Zbj6mXfAdYYKTn1JHKzJVg-yueCO9M/edit#gid=0'
# wb = gc.open_by_url(SPREADSHEET_URL)
# print(wb)

# ①「名前」で取得
ws = wb.worksheet('school Bus Uketsuke Sheet')
# ②「index」で取得
# ws = wb.get_worksheet(0)
# ③「sheet1」で取得
# ws = wb.sheet1
# print(ws)
# 100行、20列の「new worksheet」を新規作成
# ws = wb.add_worksheet(title="new worksheet", rows=100, cols=20)
# 「シート1」を「update title」に変更
# ws.update_title("school Bus Uketsuke Sheet")

# ws0 = wb.get_worksheet(0)  # update titleシート
# ws1 = wb.get_worksheet(1)  # new worksheetシート
# print(ws0.id)
# print(ws1.id)

# wb.duplicate_sheet(source_sheet_id = 957547212, new_sheet_name = "second worksheet")
# wb.duplicate_sheet(source_sheet_id = 957547212, new_sheet_name = "second worksheet", insert_sheet_index = 2)
# wb.duplicate_sheet(source_sheet_id = ws1.id, new_sheet_name = "second worksheet", insert_sheet_index = len(wb.worksheets()))

# ワークシートをすべて取得する
# print(wb.worksheets())

# ワークシート（second worksheet）を削除する
# ws = wb.get_worksheet(2)
# wb.del_worksheet(ws)

# A1表記で入力
# ws.update_acell('A1', 1)
# ws.update_acell('A2', 2)
# ws.update_acell('A3', 3)
# ws.update_acell('A4', '=SUM(A1:A3)')  # 関数も入力可能

# R1C1表記で入力
# ws.update_cell(1, 2, 4)              # B1
# ws.update_cell(2, 2, 5)              # B2
# ws.update_cell(3, 2, 6)              # B3
# ws.update_cell(4, 2, '=SUM(B1:B3)')  # B4（関数も入力可能）

# A1表記で取得
# a1 = ws.acell('A1').value  # A1（値:1）
# print(a1)
# R1C1表記で取得
# r1c1 = ws.cell(1, 2).value  # B1（値:4）
# print(r1c1)

# 複数のセルに値を入力（1行のみ）
# datas = ["A5追加", "B5追加"]
# ws.append_row(datas)
# 複数のセルに値を入力（複数行）
# datas = [
#           ["A6追加", "B6追加"],
#           ["A7追加", "B7追加"],
#         ]
# for row_data in datas:
#     ws.append_row(row_data)

# ①2行目をリストで取得
# row_list = ws.row_values(2) 
# print("--- 2行目をリストで出力 ---")
# print(row_list)
# ②2行目の2つ目（B2）の値を出力
# print("--- 2行目の2つ目（B2）の値を出力 ---")
# print(row_list[1])
# ③2行目の値を1つずつ出力
# print("--- 2行目の値を1つずつ出力 ---")
# for data in row_list:
#     print(data)

# ①2列目をリストで取得
# col_list = ws.col_values(2)
# print("--- 2列目をリストで出力 ---")
# print(col_list)
# ②2列目の2つ目（B2）の値を出力
# print("--- 2列目の2つ目（B2）の値を出力 ---")
# print(col_list[1])
# ③2列目の値を1つずつ出力
# print("--- 2列目の値を1つずつ出力 ---")
# for data in col_list:
#     print(data)

# ①全ての値（A1:B7）を二次元リストで取得
# list_of_lists = ws.get_all_values() 
# print("--- 全ての値（A1:B7）を二次元リストで出力 ---")
# print(list_of_lists)
# ②2列目の2つ目（B2）の値を出力
# print("--- 2列目の2つ目（B2）の値を出力 ---")
# print(list_of_lists[1][1])
# ③全ての値を1つずつ出力
# print("--- 全ての値を1つずつ出力 ---")
# for row_data in list_of_lists:
#     for data in row_data:
#         print(data)

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
            flex_message_json_dict = flex_message_hamurajson_dict
        elif event.message.text == "八王子西特別支援学校":
            flex_message_json_dict = flex_message_hachinishijson_dict
        elif event.message.text == "あきる野学園":
            flex_message_json_dict = flex_message_akirunojson_dict
        elif event.message.text == "七生特別支援学校":
            flex_message_json_dict = flex_message_nanaojson_dict
        elif event.message.text == "青峰学園":
            flex_message_json_dict = flex_message_seihojson_dict
        elif event.message.text == "八王子盲学校":
            flex_message_json_dict = flex_message_hachimojson_dict
        elif event.message.text == "村山特別支援学校":
            flex_message_json_dict = flex_message_murayamajson_dict
        elif event.message.text == "武蔵台学園":
            flex_message_json_dict = flex_message_musashidaijson_dict
        elif event.message.text == "田無特別支援学校":
            flex_message_json_dict = flex_message_tanashijson_dict
        elif event.message.text == "清瀬特別支援学校":
            flex_message_json_dict = flex_message_kiyosejson_dict
        elif event.message.text == "立川学園":
            flex_message_json_dict = flex_message_tachikawajson_dict
        elif event.message.text == "小金井特別支援学校":
            flex_message_json_dict = flex_message_koganeijson_dict
        elif event.message.text == "光明学園":
            flex_message_json_dict = flex_message_komeijson_dict
        elif event.message.text == "小平特別支援学校":
            flex_message_json_dict = flex_message_kodairajson_dict
        else:
            reply_message = f"{event.message.text} は、弊社では受け付けておりません。"
            repMessage(event, reply_message)
            users[userId]["mode"] = 0
            exit()
        
        users[userId]["school"] = event.message.text
        temp = 5
        ws.update.cell(2,4,temp)
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