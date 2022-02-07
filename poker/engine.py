import json
import logging
import os
import random
import itertools
import time

site  = os.environ.get("SITE_URL")

from poker.structures import currency_map, currencies, cards, card_image_name

import poker.db as db
import poker.scoring as scoring

logging.basicConfig(level=logging.DEBUG)

def maybe_add_player(slack, game_id, user, logger):
    conn = db.get_conn()

    state = db.load_game(conn, game_id)

    if state:
        if state['status'] == 'pending':
            if user not in state['players'] or True: # TODO dev hack
                logger.info('Adding player ' + user)
                state['players'].append(user)

                logger.info(state)

                if len(state['players']) > 3:
                    start_game(slack, conn, game_id, state)
                else:
                    db.save_game(conn, game_id, state)

    conn.commit()
    conn.close()

def start_game(slack, conn, game_id, state):

    # TODO dev hack
    state['players'] = ['player1', 'player2', 'player3', 'player4']
    state['handles'] = {player: state['host'] for player in state['players']}

    random.shuffle(state['players'])

    thread_ts = game_id.split("-")[1]

    order_msg = ", ".join([f"<@{state['handles'][player]}>" for player in state['players']])
    response = slack.chat_postMessage(channel='awesomeness', text=f"Game on! The order of play is {order_msg}. I'll deal.", thread_ts=thread_ts)

    deck = list(range(0, 52))

    random.shuffle(deck)
    
    player_hands = {}
    player_bets = {}
    
    for player in state['players']:
        card1 = deck.pop(0)
        card2 = deck.pop(0)
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

    deck.pop(0) # for old time's sake

    state['flop']  = [deck.pop(0), deck.pop(0), deck.pop(0)]
    state['turn']  = deck.pop(0)
    state['river'] = deck.pop(0)

    state['hands'] = player_hands
    state['bets'] = player_bets

    state['current_bet'] = state['buyin']

    state['opening-bets-complete'] = False
    state['opening-bets-idx'] = -1
    state['opening-bets-round-trip'] = False

    state['flop-bets-complete'] = False
    state['flop-bets-idx'] = -1
    state['flop-bets-round-trip'] = False

    state['turn-bets-complete'] = False
    state['turn-bets-idx'] = -1
    state['turn-bets-round-trip'] = False

    state['river-bets-complete'] = False
    state['river-bets-idx'] = -1
    state['river-bets-round-trip'] = False

    state['folded'] = []

    state['status'] = 'in-progress'

    payload = {
      'player': None,
      'thread_ts': thread_ts,
      'game_id': game_id
    }

    advance_play(slack, conn, payload, state)
    
    db.save_game(conn, game_id, state)

def fold(slack, user, name, payload):

    conn = db.get_conn()
    state = db.load_game(conn, payload['game_id'])

    state['folded'].append(payload['player'])

    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} folds", thread_ts=payload['thread_ts'])

    advance_play(slack, conn, payload, state)

    db.save_game(conn, payload['game_id'], state)

    conn.commit()
    conn.close()

def check(slack, user, name, payload, logger):

    conn = db.get_conn()
    state = db.load_game(conn, payload['game_id'])

    state['bets'][payload['player']] = state['current_bet']

    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} checks", thread_ts=payload['thread_ts'])

    logger.info(state) 

    advance_play(slack, conn, payload, state)
    
    logger.info(state) 

    db.save_game(conn, payload['game_id'], state)

    conn.commit()
    conn.close()

def single(slack, user, name, payload):

    conn = db.get_conn()
    state = db.load_game(conn, payload['game_id'])

    state['current_bet'] = state['current_bet'] + state['buyin']

    state['bets'][payload['player']] = state['current_bet']

    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} raises {state['buyin']}", thread_ts=payload['thread_ts'])

    advance_play(slack, conn, payload, state)

    db.save_game(conn, payload['game_id'], state)

    conn.commit()
    conn.close()

def double(slack, user, name, payload):

    conn = db.get_conn()
    state = db.load_game(conn, payload['game_id'])

    state['current_bet'] = state['current_bet'] + state['buyin']

    state['bets'][payload['player']] = state['current_bet'] * 2

    response = slack.chat_postMessage(channel='awesomeness', text=f"{payload['player']} raises {state['buyin'] * 2}", thread_ts=payload['thread_ts'])

    advance_play(slack, conn, payload, state)

    db.save_game(conn, payload['game_id'], state)

    conn.commit()
    conn.close()

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

def advance_play(slack, conn, payload, state):

    if len(state['folded']) >= len(state['players']) - 1:
        finish_game(slack, conn, payload, state)
        return

    if not state['opening-bets-complete']:
        phase = 'opening'
    elif not state['flop-bets-complete']:
        phase = 'flop'
    elif not state['turn-bets-complete']:
        phase = 'turn'
    elif not state['river-bets-complete']:
        phase = 'river'
    else:
        phase = 'endgame'

    if phase != 'endgame':

        next_player_idx = (state.get(f'{phase}-bets-idx', -1) + 1)

        if next_player_idx == len(state['players']):
            next_player_idx = 0
            state[f'{phase}-bets-round-trip'] = True

        # Skip over folded players
        while state['players'][next_player_idx] in state['folded']:
            next_player_idx = next_player_idx + 1

            if next_player_idx == len(state['players']):
                next_player_idx = 0
                state[f'{phase}-bets-round-trip'] = True

        outstanding_bet = state['bets'][state['players'][next_player_idx]] < state['current_bet']

        if outstanding_bet or not state[f'{phase}-bets-round-trip']:
            state[f'{phase}-bets-idx'] = next_player_idx
            state['current_player']   = state['players'][next_player_idx]
            payload['player'] = state['current_player']
            blocks = get_bet_blocks(payload)
            time.sleep(2)
            response = slack.chat_postEphemeral(channel='awesomeness', thread_ts=payload['thread_ts'], blocks=blocks, user=state['handles'][state['current_player']])
        else:
            if phase == 'opening':
                blocks = [
                    {
                       "title": {
                          "type": "plain_text",
                          "text": f"Here's the flop!"
                        },
                        "type": "image",
                        "image_url": f"https://{site}/static/" + card_image_name(state['flop'][0]),
                        "alt_text": "A poker card"
                    },
                    {
                   
                        "type": "image",
                        "image_url": f"https://{site}/static/" + card_image_name(state['flop'][1]),
                        "alt_text": "A poker card"
                    },
                    {
                   
                        "type": "image",
                        "image_url": f"https://{site}/static/" + card_image_name(state['flop'][2]),
                        "alt_text": "A poker card"
                    }
                ]
    
                response = slack.chat_postMessage(channel='awesomeness', blocks=blocks, thread_ts=payload['thread_ts'])
    
            elif phase == 'flop':
                blocks = [
                    {
                       "title": {
                          "type": "plain_text",
                          "text": f"The turn"
                        },
                        "type": "image",
                        "image_url": f"https://{site}/static/" + card_image_name(state['turn']),
                        "alt_text": "A poker card"
                    }
                ]
    
                response = slack.chat_postMessage(channel='awesomeness', blocks=blocks, thread_ts=payload['thread_ts'])

            elif phase == 'turn':
                blocks = [
                    {
                       "title": {
                          "type": "plain_text",
                          "text": f"Last, but not least: The River"
                        },
                        "type": "image",
                        "image_url": f"https://{site}/static/" + card_image_name(state['river']),
                        "alt_text": "A poker card"
                    }
                ]
    
                response = slack.chat_postMessage(channel='awesomeness', blocks=blocks, thread_ts=payload['thread_ts'])
               
            state[f'{phase}-bets-complete'] = True

            advance_play(slack, conn, payload, state)

    else:
        finish_game(slack, conn, payload, state)

def finish_game(slack, conn, payload, state):
    state['status'] = 'complete'

    folded = state['folded']
    active = [player for player in state['players'] if player not in state['folded']]

    if len(active) == 1:
        winner = active[0]
        text = f"Go ahead and rest on your laurels <@{state['handles'][winner]}> ({winner}) - you won!"
        for player in folded:
            text += f"\n- <@{state['handles'][player]}> ({player}) owes {state['bets'][player]} {state['currency']}"
        response = slack.chat_postMessage(channel='awesomeness', text=text, thread_ts=payload['thread_ts'], reply_broadcast=True)
    else:

        results = []

        for player in active:
            all_cards = state['hands'][player] +  state['flop'] + [state['turn'], state['river']]
            assert len(all_cards) == 7

            best = None

            for hand in itertools.combinations(all_cards, 5): 
   
                b = scoring.best(hand)
                s = ''.join([scoring.ord_lexico[i] for i in b])

                results.append({'lex': s, 'player': player})

        results = list(reversed(sorted(results, key=lambda d: d['lex'])))
        winners = set([results[0]['player']])

        for res in results[1:]:
            if res['lex'] == results[0]['lex']:
                winners.add(res['player'])
            else:
                break
                
        if len(winners) == 1:
            winner = list(winners)[0]
            text = f"Go ahead and rest on your laurels <@{state['handles'][winner]}> ({winner}) - you won with a {scoring.hands[int(results[0]['lex'][0])]['name']}"
            for player in [player for player in state['players'] if player != winner]:
                text += f"\n- <@{state['handles'][player]}> ({player}) owes {state['bets'][player]} {state['currency']}"
            response = slack.chat_postMessage(channel='awesomeness', text=text, thread_ts=payload['thread_ts'], reply_broadcast=True)
        else:
            text = f"Whoa - we had a tie: " + " and ".join([f"<@{state['handles'][player]}>" for player in winners]) + " can take a break"
            for player in [player for player in state['players'] if player not in winners]:
                text += f"\n- <@{state['handles'][player]}> ({player}) owes {state['bets'][player]} {state['currency']}"
            response = slack.chat_postMessage(channel='awesomeness', text=text, thread_ts=payload['thread_ts'], reply_broadcast=True)

        