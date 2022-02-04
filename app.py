from flask import Flask

from poker.cards import cards

app = Flask(__name__)

@app.route("/")
def index():
    return {'cards': cards}
