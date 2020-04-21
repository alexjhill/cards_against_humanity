from flask import Flask, render_template, request, redirect, url_for, make_response
from jinja2 import Template
import pymongo
from pymongo import MongoClient, ReturnDocument
import random
import coloredlogs, logging
app = Flask(__name__)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

DB_URI = 'mongodb://admin:password1@ds115573.mlab.com:15573/cards-against-humanity?retryWrites=false'

client = MongoClient(DB_URI)
db = client['cards-against-humanity']


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
        db.cards.insert_one(new_card)
        return render_template("add-cards.html")
    else:
        return render_template("add-cards.html")

@app.route('/set_name', methods=['GET', 'POST'])
def set_name(): # set player name if player hasn't done so before
    if request.method == 'POST':
        name = request.form.get("name")
        player_id = create_id(8)
        player = {
            "_id": player_id,
            "name": name,
            "cards": []
        }
        db.players.insert_one(player)
        game_id = request.cookies.get('game_id')
        resp = make_response(redirect(url_for("game", game_id = game_id)))
        resp.set_cookie('player_id', player_id)
        return resp
    else:
        return render_template("set-name.html")

@app.route('/new_game')
def new_game():
    player_id = request.cookies.get('player_id')
    db.players.update_one({"_id": player_id}, {"$set": {"cards": []}})
    game_id = create_id(5)
    while db.games.find_one({"_id": game_id}) is not None:
        logger.warning("Game ID already exists")
        game_id = create_id(5)
    new_game = {"_id": game_id, "players" : []}
    db.games.insert_one(new_game)
    return redirect(url_for("game", game_id = game_id))



@app.route('/game/<game_id>')
def game(game_id):
    is_card_tzar = False
    player_id = request.cookies.get('player_id')
    # if player has not been here before
    if player_id is None:
        # create new name
        response = redirect(url_for("set_name"))
        response.set_cookie('game_id', game_id)
        return response
    else:
        # add player to game
        player = db.players.find_one({"_id": player_id})
        db.games.update({"_id": game_id}, {"$push": {"players": player}})

        # get game object
        game = db.games.find_one({"_id": game_id})

        # get players
        players = game.get("players")
        if not player.get("cards"):
            random_cards = []
            for i in range(0, 10):
                rand = random.randint(0, db.cards.count())
                random_cards.append(db.cards.find().skip(rand).limit(1)[0])
            db.players.update_one({"_id": player_id}, {"$set": {"cards": random_cards}})
        cards = db.players.find_one({"_id": player_id}).get("cards")
        return render_template("game.html", game = game, players = players, cards = cards, is_card_tzar = is_card_tzar)


@app.route('/game/play_card')
def play_card(card_id):
    game_id = request.cookies.get('game_id')
    redirect(url_for("game"), game_id = game_id)
