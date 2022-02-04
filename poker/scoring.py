import itertools

from collections import defaultdict

from poker.cards import cards

####################### Helpers #######################

def is_flush(hand):
  if len(set([cards[c]['suit'] for c in hand])) == 1:
     return True

  return False

def is_straight(hand):
  ords = sorted([cards[c]['ordinal'] for c in hand])

  return ords == list(range(min(ords), max(ords) + 1))

def is_x_of_a_kind(hand, x):
  ord_counts = defaultdict(lambda: 0)

  for card in [cards[c] for c in hand]:
    ord_counts[card['ordinal']] += 1

  for ord, count in ord_counts.items():
    if count == x:
      return (True, ord)

  return (False, None)

def max_ordinal(hand):
    return max([cards[c]['ordinal'] for c in hand])

def to_ords(hand):
    return [cards[c]['ordinal'] for c in hand]

####################### Hand Checks #######################

def royal_flush(hand):

  if not is_flush(hand):
    return(False, [])

  if set([cards[c]['ordinal'] for c in hand]) != set([10, 11, 12, 13, 14]):
    return (False, [])

  # Holy shit nuggets
  return (True, [])

def straight_flush(hand):
  if is_flush(hand) and is_straight(hand):
      return (True, [max_ordinal(hand)])

  return (False, [])

def four_of_a_kind(hand):
  result = is_x_of_a_kind(hand, 4)

  if result[0]:
    last_card = [c for c in hand if cards[c]['ordinal'] != result[1]]
    assert len(last_card) == 1
    last_card = to_ords(last_card)[0]
    return (True, [result[1], last_card])
  
  return (False, [])

def full_house(hand):

  three = is_x_of_a_kind(hand, 3)

  if three[0]:
    remaining = [c for c in hand if cards[c]['ordinal'] != three[1]]
    assert len(remaining) == 2

    two = is_x_of_a_kind(remaining, 2)

    if two[0]:
      return (True, [three[1], two[1]])

  return (False, [])

def flush(hand):

  if is_flush(hand):
    return (True, list(reversed(sorted(to_ords(hand))))) 

  return (False, [])

def straight(hand):

  if is_straight(hand):
    return (True, [max_ordinal(hand)])

  return (False, [])

def three_of_a_kind(hand):

  three = is_x_of_a_kind(hand, 3)

  if three[0]:
    remaining = [c for c in hand if cards[c]['ordinal'] != three[1]]
    assert len(remaining) == 2
    remaining = to_ords(remaining)
    return (True, [three[1], max(remaining), min(remaining)])

  return (False, [])

def two_pair(hand):

  pair1 = is_x_of_a_kind(hand, 2)

  if pair1[0]:
    
    remaining = [c for c in hand if cards[c]['ordinal'] != pair1[1]]
    assert len(remaining) == 3

    pair2 = is_x_of_a_kind(remaining, 2)

    if pair2[0]:
      both = [pair1[1], pair2[1]]
      last_card = [c for c in remaining if cards[c]['ordinal'] != pair2[1]]
      assert len(last_card) == 1
      last_card = to_ords(last_card)[0]
      return (True, [max(both), min(both), last_card])

  return (False, [])

def pair(hand):

  pair = is_x_of_a_kind(hand, 2)

  if pair[0]:
    remaining = [c for c in hand if cards[c]['ordinal'] != pair[1]]
    assert len(remaining) == 3
    return (True, [pair[1]] +  list(reversed(sorted(to_ords(remaining)))))

  return (False, [])

def high_card(hand):
  return (True, list(reversed(sorted([cards[c]['ordinal'] for c in hand]))))
  
# The order in which hands are evaluated is super important yo. Don't reorder this list

hands = [
  {'name': 'High Card',      'rank_len': 5, 'func': high_card},
  {'name': 'Pair',           'rank_len': 4, 'func': pair},
  {'name': 'Two Pair',       'rank_len': 3, 'func': two_pair},
  {'name': 'Three of a Kind','rank_len': 3, 'func': three_of_a_kind},
  {'name': 'Straight',       'rank_len': 1, 'func': straight},
  {'name': 'Flush',          'rank_len': 5, 'func': flush},
  {'name': 'Full House',     'rank_len': 2, 'func': full_house},
  {'name': 'Four of a Kind', 'rank_len': 2, 'func': four_of_a_kind},
  {'name': 'Straight Flush', 'rank_len': 1, 'func': straight_flush},
  {'name': 'Royal Flush',    'rank_len': 0, 'func': royal_flush},
]

def best(hand):
  for hand_rank, defn in reversed(list(enumerate(hands))):
    check = defn['func'](hand)

    assert check[0] in [True, False]
    assert isinstance(check[1], list)

    if check[0]:
      assert len(check[1]) == defn['rank_len']
      return [hand_rank] + check[1]

  assert False

# This literally takes a minute
def test():
  # Hacky thing so I can just use standard string sorting to enumerate hands according
  # to their rank (relative to one another)
  ord_lexico = {
    2:  '2',
    3:  '3',
    4:  '4', 
    5:  '5', 
    6:  '6',
    7:  '7', 
    8:  '8',
    9:  '9',
    10:  'A',
    11:  'B',
    12:  'C',
    13:  'D',
    14:  'E'
  }

  hand_count   = defaultdict(lambda: 0)
  hands_actual = defaultdict(lambda: [])

  counter = 0

  for hand in itertools.combinations(range(0, 52), 5):

      result = best(hand)

      counter += 1
      hand_count[result[0]] += 1

      s = " ".join([str(cards[c]['ordinal']) + cards[c]['suit'][0] for c in hand])
      hands_actual[result[0]].append((s, ":".join([ord_lexico[i] for i in result[1:]])))

  for idx, defn in enumerate(hands):
    print(defn['name'] + ': ' + str(hand_count[idx]))

  print(counter)

  assert hand_count[9] == 4
  assert hand_count[8] == 32
  assert hand_count[7] == 624
  assert hand_count[6] == 3744
  assert hand_count[5] == 5112
  assert hand_count[4] == 9180
  assert hand_count[3] == 54912
  assert hand_count[2] == 123552
  assert hand_count[1] == 1098240
  assert hand_count[0] == 1303560

  for hand, actuals in hands_actual.items():
    actuals.sort(key=lambda x: x[1])
    with open(hands[hand]['name'] + ".txt", 'w') as f:
      for line in actuals:
        f.write("  ".join(line))
        f.write('\n')
