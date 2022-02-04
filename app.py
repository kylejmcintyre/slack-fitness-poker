import logging
import os

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

from poker.structures import currency_map, currencies, cards

import poker.db as db

logging.basicConfig(level=logging.DEBUG)

site  = os.environ.get("SITE_URL")
token = os.environ.get("SLACK_BOT_TOKEN")

app = Flask(__name__, static_url_path='/static')
bolt = App()
handler = SlackRequestHandler(bolt)

slack = WebClient(token=token)

@app.route("/bolt", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.route("/")
def index():
    blocks = [
        {
           "title": {
                "type": "plain_text",
                "text": "Here's the river:"
            },
            "type": "image",
            "image_url": f"https://{site}/static/2_of_clubs.png",
            "alt_text": "An incredibly cute kitten."
        },
        {
   
            "type": "image",
            "image_url": f"https://{site}/static/3_of_clubs.png",
            "alt_text": "An incredibly cute kitten."
        }

    ]

    slack.chat_postMessage(channel='awesomeness', blocks=blocks)
    return {'cards': cards}


@bolt.command("/game")
def poker_cmd(ack, respond, command, logger):
    ack()

    logger.debug(command)

    user = command['user_id']
    cmd  = command['text'] if 'text' in command else 'pushups 5'
    pieces = cmd.split()

    if len(pieces) != 2:
        respond(response_type="ephemeral", text="I didn't get that. Try something like `/poker pushups 5`")
        return

    currency = pieces[0]
    buyin    = pieces[1]

    if currency.lower() not in currency_map:
        respond(response_type="ephemeral", text=f"I don't know this '{currency}' you speak of. Try one of these: " + ", ".join(set(currency_map.values())))
        return

    currency = currency_map[currency]

    if not buyin.isnumeric():
        respond(response_type="ephemeral", text="I didn't get that. Try something like `/poker pushups 5`")
        return

    response = slack.chat_postMessage(channel='awesomeness', text=f"<@{user}> wants to play {currencies[currency]['singular']} poker. The buy-in is {buyin} {currency}. Who's in?")

    game_id = f"{response['channel']}-{response['ts']}"

    logger.info(f"Initializing a game: {game_id}")

    conn = db.get_conn()
    db.save_game(conn, game_id, {"foo": "bar"})
    conn.commit()
    conn.close()

@bolt.event('reaction_added')
def handle_event(event, logger):
    logger.info(event)

    if event['item']['type'] != 'message':
        return

    game_id = f"{event['item']['channel']}-{event['item']['ts']}"

    logger.info(f"Checking for a game associated with reaction: {game_id}")

    conn = db.get_conn()

    state_opt = db.load_game(conn, game_id)

    if state_opt:
        logger.info(state_opt)

    conn.close()
