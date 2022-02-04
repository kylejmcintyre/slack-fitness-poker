import os

from flask import Flask, request

from slack_sdk import WebClient

from poker.cards import cards

app = Flask(__name__, static_url_path='/static')

token=os.environ.get("SLACK_BOT_TOKEN")

slack = WebClient(token=token)

currencies = {
  "push-ups": {
    "singular": "push-up",
  },
  "sit-ups": {
    "singular": "sit-up",
  }
}

currency_map = {
  'push-up': 'push-ups',
  'pushup': 'push-ups',
  'pushups': 'push-ups',
  'push-ups': 'push-ups',
  'situp': 'sit-ups',
  'sit-up': 'sit-ups',
  'situps': 'sit-ups',
  'sit-ups': 'sit-ups',
  #'planking': 'planking',
  #'plank': 'planking'
}

site = os.environ.get("SITE_URL")

@app.route("/")
def index():
    attachments = [
      {
        "fallback": "A playing card",
        "image_url": f"https://{site}/static/2_of_spades.png",
      },
      {
        "fallback": "A playing card",
        "image_url": f"https://{site}/static/8_of_hearts.png",
      },
      {
        "fallback": "A playing card",
        "image_url": "https://{site}/static/8_of_clubs.png",
      },
    ]
    slack.chat_postMessage(channel='awesomeness', text=f"Here's the river:", attachments=attachments)
    return {'cards': cards}

@app.route("/slash-cmd", methods=["POST"])
def slash_cmd():

    # TODO verify authenticity

    user = request.form['user_id']
    cmd  = request.form['text']

    pieces = cmd.split()

    if len(pieces) != 2:
        return {
            "response_type": "ephemeral",
            "text": "I didn't get that. Try something like `/poker pushups 5`",
            "channel": 'awesomeness'
        
        } 

    currency = pieces[0]
    buyin    = pieces[1]

    if currency.lower() not in currency_map:
        return {
            "response_type": "ephemeral",
            "text": f"I don't know this '{currency}' you speak of. Try one of these: " + ", ".join(set(currency_map.values())),
            "channel": 'awesomeness'
        }

    currency = currency_map[currency]

    if not buyin.isnumeric():
        return {
            "response_type": "ephemeral",
            "text": "I didn't get that. Try something like `/poker pushups 5`",
            "channel": 'awesomeness'
        } 

    slack.chat_postMessage(channel='awesomeness', text=f"<@{user}> wants to play {currencies[currency]['singular']} poker. The buy-in is {buyin} {currency}. Who's in?")

    return {"text": "Coming right up captain"}

@app.route("/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

