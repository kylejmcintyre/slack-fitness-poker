import json
import logging
import os
import random
import time

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

from poker.structures import currency_map, currencies, cards

import poker.db as db
import poker.engine as engine

logging.basicConfig(level=logging.DEBUG)

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
    return {'cards': cards}

@bolt.command("/game")
def poker_cmd(ack, respond, command, logger):
    ack()

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

    response = slack.chat_postMessage(channel='fitness-poker', text=f"<@{user}> wants to play {currencies[currency]['singular']} poker 💪. The buy-in is {buyin} {currency}. Who's in?")

    game_id = f"{response['channel']}-{response['ts']}"

    logger.info(f"Initializing a game: {game_id}")

    state = {
      'host': user,
      'currency': currency,
      'buyin': int(buyin),
      'status': 'pending',
      'players': [user],
    }

    conn = db.get_conn()
    db.save_game(conn, game_id, state)
    conn.commit()
    conn.close()

@bolt.event('reaction_added')
def handle_reaction(event, logger):
    logger.info(event)

    if event['item']['type'] != 'message':
        return

    game_id = f"{event['item']['channel']}-{event['item']['ts']}"

    engine.maybe_add_player(slack, game_id, event['user'], logger)

@bolt.action("fold")
def handle_fold_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    engine.fold(slack, body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))

@bolt.action("check")
def handle_check_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    engine.check(slack, body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']), logger)

@bolt.action("raise")
def handle_raise_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    engine.single(slack, body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))

@bolt.action("double")
def handle_double_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    engine.double(slack, body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))
