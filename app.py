from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('LLaHIWKNBgwVlozdgSFtk3hYMa04AfYtEdGvXyYMIWZIIMUaZspah844LxKvxbARfEcKr0J8BeNi6jC47Eww4jbBu/lF43MgGJiwufZyL2XLP4J0bZXl+PDZVY5FOPg0kfQT4aYT3DZxj3fG3s/s/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d88565cbfef0134d3637555c856849de')

@app.route("/")
def test():
    return "OK"

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
    if event.message.text == "ぬるぽ":
        reply_message = "ｶﾞｯ"
    elif event.message.text == "乗車受付":
        reply_message = "学校名を入力してください。"
        if not userId in users:
            users[userId] = {}
            users[userId]["result"] = ""
    elif event.message.text == "羽村特別支援学校":
        users[userId]["school"] = event.message.text
        reply_message = "コース名を入力してください。"
    elif event.message.text == "旧青梅":
        users[userId]["cource"] = event.message.text
        reply_message = "氏名を入力してください。"
    else:
        users[userId]["shimei"] = event.message.text
        reply_message = f"{users[userId]['school']}、{users[userId]['cource']}、{users[userId]['shimei']}"

    # 例    
    # elif event.message.text == "勉強開始":
    #     reply_message = "計測を開始しました。"
    #     if not userId in users:
    #         users[userId] = {}
    #         users[userId]["total"] = 0
    #     users[userId]["start"] = time()
    # elif event.message.text == "勉強終了":
    #     end = time()
    #     difference = int(end - users[userId]["start"])
    #     users[userId]["total"] += difference
    #     hour = difference // 3600
    #     minute = (difference % 3600) //60
    #     second = difference % 60
    #     reply_message = f"勉強時間は,「 {hour}時間{minute}分{second}秒 」でした。おつかれさん！合計で{users[userId]['total']}秒勉強しています。"
    # 例の終了

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))

if __name__ == "__main__":
    app.run()