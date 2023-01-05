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

def card_image_name(card):
    defn = cards[card]

    return defn['name'].lower() + "_of_" + defn['suit'].lower() + ".png"

def card_textual_rep(card):
    defn = cards[card]

    emoji = None

    if defn['suit'] == 'Clubs':
        emoji = "♣️"
    elif defn['suit'] == 'Spades':
        emoji = "♠️"
    elif defn['suit'] == 'Hearts':
        emoji = "♥️"
    elif defn['suit'] == 'Diamonds':
        emoji = "♦️"

    ord = defn['name'][0] if defn['name'] != "10" else "10"

    return "*" + ord + "*" + emoji

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

leagues = {
  "push-up": {
    "fitness": True,
    "units": "push-ups",
    "buyin": 5,
    "synonyms": ["pushup", "pushups", "push-ups"]
  },
  "sit-up": {
    "fitness": True,
    "units": "sit-ups",
    "buyin": 5,
    "synonyms": ["situp", "situps", "sit-ups"]
  },
  "burpee": {
    "fitness": True,
    "units": "burpees",
    "buyin": 5,
    "synonyms": ["burpees"]
  },
  "squat": {
    "fitness": True,
    "units": "squats",
    "buyin": 5,
    "synonyms": ["squats"]
  },
  "plank": {
    "fitness": True,
    "units": "seconds",
    "buyin": 15,
    "synonyms": ["planks", "planking"]
  },
  "knuckle-up": {
    "fitness": True,
    "units": "knuckle-ups",
    "buyin": 5,
    "synonyms": ["knuckleup", "knuckleups", "knuckle-ups"]
  },
  "rupee": {
    "fitness": False,
    "units": "rupees",
    "buyin": 5,
    "synonyms": ["rupees"]
  },
  "chin-up": {
    "fitness": True,
    "units": "chin-ups",
    "buyin": 2,
    "synonyms": ["chin-ups", "chinups"]
  }
}
