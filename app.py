import json
import logging
import os
import random
import time

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

from poker.structures import leagues
from poker.db import Connection

import poker.engine as engine

logging.basicConfig(level=logging.DEBUG)

token = os.environ.get("SLACK_BOT_TOKEN")
channel = os.environ.get("SLACK_CHANNEL")

app = Flask(__name__, static_url_path='/static')
bolt = App()
handler = SlackRequestHandler(bolt)

slack = WebClient(token=token)

@app.route("/bolt", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.route("/")
def index():
    return {}

@bolt.command("/game")
def poker_cmd(ack, respond, command, logger):
    ack()

    user = command['user_id']
    cmd  = command['text'] if 'text' in command else ''
    pieces = cmd.split()


    if len(pieces) != 1:
        league_opts = "|".join(list(leagues.keys()))
        respond(response_type="ephemeral", text=f"Which league do you want to play in? Try something like `/game [{league_opts}]`")
        return

    league_in = pieces[0]
    league = None

    if league_in.lower().strip() == 'random':
        choices = list(leagues.keys())
        league = random.choice(choices)
    else:
        for name, league_data in leagues.items():
            if league_in == name or league_in in league_data['synonyms']:
                league = name
                break

    if league is None:
        respond(response_type="ephemeral", text=f"I don't know this '{league_in}' you speak of. Try one of these: " + ", ".join(list(leagues.keys())) + " or random")
        return

    league_data = leagues[league]

    buyin = league_data['buyin']
    units = league_data['units']

    if league_data['fitness']:
        emoji = "💪"
    else:
        emoji = "💎"
  
    if league_in.lower().strip() == 'random':
        response = slack.chat_postMessage(channel=channel, text=f"<@{user}> rolled the 🎲 on a random game and the result is {league} poker {emoji}! The buy-in is {buyin} {units}. Who's in?")
    else: 
        response = slack.chat_postMessage(channel=channel, text=f"<@{user}> wants to play {league} poker {emoji} . The buy-in is {buyin} {units}. Who's in?")

    game_id = f"{response['channel']}-{response['ts']}"

    logger.info(f"Initializing a game: {game_id}")

    state = {
      'host': user,
      'league': league,
      'buyin': int(buyin),
      'status': 'pending',
      'players': [user],
    }

    with Connection() as conn:
        conn.save_game(game_id, state)
        conn.commit()

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

    logger.info(body)

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

@bolt.action("triple")
def handle_triple_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    engine.triple(slack, body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))
