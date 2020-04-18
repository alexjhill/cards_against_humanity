from flask import Flask, render_template, request, redirect, url_for, make_response
from jinja2 import Template
import pymongo
from pymongo import MongoClient
import random
import coloredlogs, logging
app = Flask(__name__)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

DB_URI = 'mongodb://admin:password1@ds115573.mlab.com:15573/cards-against-humanity?retryWrites=false'

client = MongoClient(DB_URI)
db = client['cards-against-humanity']
games = db.games
cards = db.cards


def create_id(id_length):
    game_id = ''
    characters = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    for i in range(id_length):
        game_id += random.choice(characters)
    return game_id



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/add_cards', methods=['GET', 'POST'])
def add_cards():
    if request.method == 'POST':
        text = request.form.get("card-text")
        new_card = {"text": text}
        cards.insert_one(new_card)
        return render_template("add-cards.html")
    else:
        return render_template("add-cards.html")


@app.route('/new_game')
def new_game():
    game_id = create_id(5)
    while games.find_one({"_id": game_id}) is not None:
        logger.warning("Game ID already exists")
        game_id = create_id(5)
    new_game = {"_id": game_id}
    games.insert_one(new_game)
    resp = make_response(redirect(url_for("game", game_id = game_id)))
    resp.set_cookie('user_id', create_id(8))
    return resp



@app.route('/<game_id>')
def game(game_id):
    game = games.find_one({"_id": game_id})
    user_id = request.cookies.get('user_id')
    print(user_id)
    user_cards = cards.find({"user": user_id})
    return render_template("game.html", user_cards=user_cards)
