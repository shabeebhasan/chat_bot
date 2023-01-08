from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

DEBUG = os.getenv("DEBUG",1)
openai.api_key = os.getenv("OPENAI_API_KEY")
# This is page access token that you get from facebook developer console.
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
# This is API key for facebook messenger.
API = "https://graph.facebook.com/v13.0/me/messages?access_token="+PAGE_ACCESS_TOKEN

# This function use for verify token with facebook webhook. So we can verify our flask app and facebook are connected.
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/", methods=['GET'])
def fbverify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200
    return "Hello world", 200

@app.route("/test-ai", methods=['GET'])
def testai():
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt="hi",
      temperature=0.9,
      max_tokens=150,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
    )
    return response['choices'][0]['text'], 200

# This function return response to facebook messenger.

@app.route("/", methods=['POST'])
def fbwebhook():
    data = request.get_json()
    print("request",request)
    print("request",data)
    # Read messages from facebook messanger.
    message = data['entry'][0]['messaging'][0]['message']
    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    print("sender_id",message['text'])
    print("sender_id",sender_id)
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt= message['text'],
      temperature=0.9,
      max_tokens=150,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.6,
      stop=[" Human:", " AI:"]
    )
    print(response)
    response_ai = response['choices'][0]['text']
    request_body = {
     "recipient": {
        "id": sender_id
      },
      "message": {
        "text": response_ai
      }
    }
    response_return = requests.post(API, json=request_body).json()
    return response_return


if __name__ == "__main__":
    app.run(debug=DEBUG)
