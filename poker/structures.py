# Position in this list is the card's identity. Don't reorder this list.

cards = [
  {"suit": "Spades",   "name": "2",     "ordinal": 2},
  {"suit": "Spades",   "name": "3",     "ordinal": 3},
  {"suit": "Spades",   "name": "4",     "ordinal": 4},
  {"suit": "Spades",   "name": "5",     "ordinal": 5},
  {"suit": "Spades",   "name": "6",     "ordinal": 6},
  {"suit": "Spades",   "name": "7",     "ordinal": 7},
  {"suit": "Spades",   "name": "8",     "ordinal": 8},
  {"suit": "Spades",   "name": "9",     "ordinal": 9},
  {"suit": "Spades",   "name": "10",    "ordinal": 10},
  {"suit": "Spades",   "name": "Jack",  "ordinal": 11},
  {"suit": "Spades",   "name": "Queen", "ordinal": 12},
  {"suit": "Spades",   "name": "King",  "ordinal": 13},
  {"suit": "Spades",   "name": "Ace",   "ordinal": 14},
  {"suit": "Diamonds", "name": "2",     "ordinal": 2},
  {"suit": "Diamonds", "name": "3",     "ordinal": 3},
  {"suit": "Diamonds", "name": "4",     "ordinal": 4},
  {"suit": "Diamonds", "name": "5",     "ordinal": 5},
  {"suit": "Diamonds", "name": "6",     "ordinal": 6},
  {"suit": "Diamonds", "name": "7",     "ordinal": 7},
  {"suit": "Diamonds", "name": "8",     "ordinal": 8},
  {"suit": "Diamonds", "name": "9",     "ordinal": 9},
  {"suit": "Diamonds", "name": "10",    "ordinal": 10},
  {"suit": "Diamonds", "name": "Jack",  "ordinal": 11},
  {"suit": "Diamonds", "name": "Queen", "ordinal": 12},
  {"suit": "Diamonds", "name": "King",  "ordinal": 13},
  {"suit": "Diamonds", "name": "Ace",   "ordinal": 14},
  {"suit": "Hearts",   "name": "2",     "ordinal": 2},
  {"suit": "Hearts",   "name": "3",     "ordinal": 3},
  {"suit": "Hearts",   "name": "4",     "ordinal": 4},
  {"suit": "Hearts",   "name": "5",     "ordinal": 5},
  {"suit": "Hearts",   "name": "6",     "ordinal": 6},
  {"suit": "Hearts",   "name": "7",     "ordinal": 7},
  {"suit": "Hearts",   "name": "8",     "ordinal": 8},
  {"suit": "Hearts",   "name": "9",     "ordinal": 9},
  {"suit": "Hearts",   "name": "10",    "ordinal": 10},
  {"suit": "Hearts",   "name": "Jack",  "ordinal": 11},
  {"suit": "Hearts",   "name": "Queen", "ordinal": 12},
  {"suit": "Hearts",   "name": "King",  "ordinal": 13},
  {"suit": "Hearts",   "name": "Ace",   "ordinal": 14},
  {"suit": "Clubs",    "name": "2",     "ordinal": 2},
  {"suit": "Clubs",    "name": "3",     "ordinal": 3},
  {"suit": "Clubs",    "name": "4",     "ordinal": 4},
  {"suit": "Clubs",    "name": "5",     "ordinal": 5},
  {"suit": "Clubs",    "name": "6",     "ordinal": 6},
  {"suit": "Clubs",    "name": "7",     "ordinal": 7},
  {"suit": "Clubs",    "name": "8",     "ordinal": 8},
  {"suit": "Clubs",    "name": "9",     "ordinal": 9},
  {"suit": "Clubs",    "name": "10",    "ordinal": 10},
  {"suit": "Clubs",    "name": "Jack",  "ordinal": 11},
  {"suit": "Clubs",    "name": "Queen", "ordinal": 12},
  {"suit": "Clubs",    "name": "King",  "ordinal": 13},
  {"suit": "Clubs",    "name": "Ace",   "ordinal": 14},
]

assert len([c for c in cards if c['suit'] == "Clubs"]) == 13
assert len([c for c in cards if c['suit'] == "Diamonds"]) == 13
assert len([c for c in cards if c['suit'] == "Hearts"]) == 13
assert len([c for c in cards if c['suit'] == "Spades"]) == 13

from collections import defaultdict

ord_counts = defaultdict(lambda: 0)

for c in cards:
  ord_counts[c['ordinal']] += 1

for key, value in ord_counts.items():
  assert value == 4

currencies = {
  "push-ups": {
    "singular": "push-up",
  },
  "sit-ups": {
    "singular": "sit-up",
  },
  "burpees": {
    "singular": "burpee",
  },
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
  'burpees': 'sit-ups',
  'burpee': 'burpees',
}


