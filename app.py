import json
import logging
import os
import random

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

from poker.structures import currency_map, currencies, cards, card_image_name

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

    response = slack.chat_postMessage(channel='awesomeness', text=f"<@{user}> wants to play {currencies[currency]['singular']} poker 💪. The buy-in is {buyin} {currency}. Who's in?")

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

    maybe_add_player(game_id, event['user'], logger)

@bolt.action("fold")
def handle_fold_action(ack, respond, body, logger):
    ack()

    respond(delete_original=True)

    fold(body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))

@bolt.action("check")
def handle_check_action(ack, body, logger):
    ack()

    respond(delete_original=True)

    check(body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))

@bolt.action("raise")
def handle_raise_action(ack, body, logger):
    ack()

    respond(delete_original=True)

    single(body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))

@bolt.action("double")
def handle_double_action(ack, body, logger):
    ack()

    respond(delete_original=True)

    double(body['user']['id'], body['user']['name'], json.loads(body['actions'][0]['value']))
    
def maybe_add_player(game_id, user, logger):
    conn = db.get_conn()

    state = db.load_game(conn, game_id)

    if state:
        if state['status'] == 'pending':
            if user not in state['players'] or True: # TODO dev hack
                logger.info('Adding player ' + user)
                state['players'].append(user)

                logger.info(state)

                if len(state['players']) > 1:
                    start_game(conn, game_id, state)
                else:
                    db.save_game(conn, game_id, state)

    conn.commit()
    conn.close()

def start_game(conn, game_id, state):

    # TODO dev hack
    state['players'] = ['player1', 'player2', 'player3', 'player4']
    state['handles'] = {player: state['host'] for player in state['players']}

    random.shuffle(state['players'])

    thread_ts = game_id.split("-")[1]

    order_msg = ", ".join([f"<@{state['handles'][player]}>" for player in state['players']])
    response = slack.chat_postMessage(channel='awesomeness', text=f"Game on! The order of play is {order_msg}. I'll deal.", thread_ts=thread_ts)

    state['deck'] = list(range(0, 52))

    random.shuffle(state['deck'])
    
    player_hands = {}
    player_bets = {}
    
    for player in state['players']:
        card1 = state['deck'].pop(0)
        card2 = state['deck'].pop(0)
        player_hands[player] = [card1, card2]
        player_bets[player] = state['buyin']
    
        blocks = [
            {
               "title": {
                  "type": "plain_text",
                  "text": f"Good luck {player} (I say that to everyone)"
                },
                "type": "image",
                "image_url": f"https://{site}/static/" + card_image_name(card1),
                "alt_text": "A poker card"
            },
            {
           
                "type": "image",
                "image_url": f"https://{site}/static/" + card_image_name(card2),
                "alt_text": "A poker card"
            }
        ]

        response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=thread_ts, blocks=blocks, user=state['handles'][player])

    state['hands'] = player_hands
    state['bets'] = player_bets

    state['current_bet'] = state['buyin']

    state['status'] = 'in-progress'

    payload = {
      'player': state['current_player'],
      'thread_ts': thread_ts,
      'game_id': game_id
    }

    payload = json.dumps(payload)

    advance_play(conn, payload, state)

def fold(user, name, payload):

    conn = db.get_conn()
    state = db.load_game(conn, payload['game_id'])

    state['folds'].append(payload['player'])

    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} folds", thread_ts=payload['thread_ts'])

    advance_play(conn, payload, state)

    conn.commit()
    conn.close()

def check(user, name, payload):
    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} checks", thread_ts=payload['thread_ts'])

def single(user, name, payload):
    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} raises", thread_ts=payload['thread_ts'])

def double(user, name, payload):
    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} doubles", thread_ts=payload['thread_ts'])

def get_bet_blocks(payload):
    payload = json.dumps(payload)
    blocks = [
        {
            "type": "actions",
            "block_id": "actions1",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Check"
                    },
                    "value": payload,
                    "action_id": "check"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Raise 5"
                    },
                    "value": payload,
                    "action_id": "raise"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Raise 10"
                    },
                    "value": payload,
                    "action_id": "double"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Fold"
                    },
                    "value": payload,
                    "action_id": "fold"
                }
            ]
        }
    ]

    return blocks

def show_flop(conn, payload, state): 
    pass

def advance_play(conn, payload, state):

    if 'opening-bets-idx' not in state or state['opening-bets-idx'] < len(state['players']):

        next_idx = state.get('opening-bets-idx', -1) + 1

        while state['players'][next_idx] in state['folded'] and next_idx < len(state['players']):
            next_idx = state.get('opening-bets-idx', -1) + 1

        state['opening-bets-idx'] = next_idx

        if next_idx < len(state['players']):
            state['current_player'] = state['players'][next_idx]
            blocks = get_bet_blocks(payload)
            response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=payload['thread_ts'], blocks=blocks, user=state['handles'][state['current_player']])
        else:
            # show the flop, recursively advance
            pass

    elif 'flop-bets-idx' not in state or state['flop-bets-idx'] < len(state['players']):
        next_idx = state.get('flop-bets-idx', -1) + 1

        while state['players'][next_idx] in state['folded'] and next_idx < len(state['players']):
            next_idx = state.get('flop-bets-idx', -1) + 1

        state['flop-bets-idx'] = next_idx

        if next_idx < len(state['players']):
            state['current_player'] = state['players'][next_idx]
            blocks = get_bet_blocks(payload)
            response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=payload['thread_ts'], blocks=blocks, user=state['handles'][state['current_player']])
        else:
            # show the turn, recursively advance
            pass

    elif 'turn-bets-idx' not in state or state['turn-bets-idx'] < len(state['players']):
        next_idx = state.get('turn-bets-idx', -1) + 1

        while state['players'][next_idx] in state['folded'] and next_idx < len(state['players']):
            next_idx = state.get('turn-bets-idx', -1) + 1

        state['turn-bets-idx'] = next_idx

        if next_idx < len(state['players']):
            state['current_player'] = state['players'][next_idx]
            blocks = get_bet_blocks(payload)
            response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=payload['thread_ts'], blocks=blocks, user=state['handles'][state['current_player']])
        else:
            # show the river, recursively advance
            pass

    elif 'river-bets-idx' not in state or state['river-bets-idx'] < len(state['players']):
        next_idx = state.get('river-bets-idx', -1) + 1

        while state['players'][next_idx] in state['folded'] and next_idx < len(state['players']):
            next_idx = state.get('river-bets-idx', -1) + 1

        state['river-bets-idx'] = next_idx

        if next_idx < len(state['players']):
            state['current_player'] = state['players'][next_idx]
            blocks = get_bet_blocks(payload)
            response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=payload['thread_ts'], blocks=blocks, user=state['handles'][state['current_player']])
        else:
            # show the river, recursively advance
            pass





    db.save_game(conn, game_id, state)
