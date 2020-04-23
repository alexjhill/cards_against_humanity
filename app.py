'''
GAME STATES
-1 = error
0 = black card selection
1 = card playing
2 = winner selection

PLAYER STATES
0 = card playing
1 = card played

'''


from flask import Flask, render_template, request, redirect, url_for, make_response
from jinja2 import Template
import pymongo
from pymongo import MongoClient, ReturnDocument
import json
from bson import json_util
import random
import coloredlogs, logging

app = Flask(__name__)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

DB_URI = 'mongodb://admin:password1@ds115573.mlab.com:15573/cards-against-humanity?retryWrites=false'

client = MongoClient(DB_URI)
db = client['cards-against-humanity']


def create_id(id_length):
    id = ''
    characters = "ABCDEFGHIJKLMOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    for i in range(id_length):
        id += random.choice(characters)
    return id



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        game_id = request.form.get("game-id")
        return redirect(url_for("game", game_id = game_id))
    else:
        return render_template("home.html")

@app.route('/add_cards', methods=['GET', 'POST'])
def add_cards():
    if request.method == 'POST':
        text = request.form.get("card-text")
        new_card = {"_id": create_id(24), "text": text}
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
            "cards": [],
            "state": 0,
            "score": 0
        }
        db.players.insert_one(player)
        game_id = request.cookies.get('game_id')
        resp = make_response(redirect(url_for("game", game_id = game_id)))
        resp.set_cookie('player_id', player_id)
        return resp
    else:
        return render_template("set-name.html")

@app.route('/new_game')
def new_game(): # create new game
    player_id = request.cookies.get('player_id')

    # reset players cards
    db.players.update_one({"_id": player_id}, {"$set": {"cards": []}})

    # create new unique game
    game_id = create_id(5)
    while db.games.find_one({"_id": game_id}) is not None:
        logger.warning("Game ID already exists")
        game_id = create_id(5)
    new_game = {
        "_id": game_id,
        "state": 0,
        "played_cards": []
    }
    db.games.insert_one(new_game)

    return redirect(url_for("game", game_id = game_id))



@app.route('/game/<game_id>')
def game(game_id):
    game = db.games.find_one({"_id": game_id})
    if game:
        is_card_tzar = False
        player_id = request.cookies.get('player_id')
        # if player has not been here before
        if player_id is None:
            # create new name
            resp = make_response(redirect(url_for("set_name")))
            resp.set_cookie('game_id', game_id)
            return resp
        else:
            # add game to player
            db.players.update_one({"_id": player_id}, {"$set": {"game": game_id}})
            resp = make_response(render_template("game.html"))
            resp.set_cookie('game_id', game_id)
            return resp
    else:
        return redirect(url_for("home"))

@app.route('/game/<game_id>/get_game')
def get_game(game_id):
    game = db.games.find_one({"_id": game_id})
    return json.dumps(game, default=json_util.default)

@app.route('/game/<game_id>/get_players')
def get_players(game_id): # return all players matching this game
    players = list(db.players.find({"game": game_id}))
    return json.dumps(players, default=json_util.default)

@app.route('/game/<game_id>/get_cards')
def get_cards(game_id): # return cards for this player
    player_id = request.cookies.get('player_id')
    player = db.players.find_one({"_id": player_id})

    # if player doesn't have cards get random ones
    if not player.get("cards"):
        random_cards = []
        for i in range(0, 10):
            rand = random.randint(0, db.cards.count())
            random_card = db.cards.find().skip(rand).limit(1)[0]
            random_cards.append(random_card)
        db.players.update_one({"_id": player_id}, {"$set": {"cards": random_cards}})

    # get player cards
    cards = db.players.find_one({"_id": player_id}).get("cards")
    return json.dumps(cards, default=json_util.default)

@app.route('/game/<game_id>/play_card', methods=['POST'])
def play_card(game_id):
    player_id = request.cookies.get('player_id')

    # get played card
    card_play = json.loads(request.data)
    db.games.update_one({"_id": game_id}, {"$push": {"played_cards": card_play}})

    # remove played card
    db.players.update_one({"_id": player_id}, {"$pull": {"cards": {"_id": card_play.get("card_id")}}})

    # try to add new card until it's unique
    while True:
        try:
            rand = random.randint(0, db.cards.count())
            new_card = db.cards.find().skip(rand).limit(1)[0]
            db.players.update_one({"_id": player_id}, {"$push": {"cards": new_card}})
            break
        except Foo:
            logger.warning("Duplicate card found")
            continue

    # update played state
    db.players.update_one({"_id": player_id}, {"$set": {"state": 1}})

    # get updated cards
    updated_cards = db.players.find_one({"_id": player_id}).get("cards")

    return json.dumps(updated_cards,default=json_util.default)


@app.route('/game/<game_id>/new_round')
def new_round(game_id):
    # wipe played cards
    db.games.update_one({"_id": game_id}, {"$push": {"played_cards": []}})
    # update played state
    db.players.update_one({"_id": player_id}, {"$set": {"state": 0}})


# @app.route('/game/remove_player', methods=['POST'])
# def remove_player():
    # logger.debug("test")
    # player_id = request.cookies.get('player_id')
    # db.players.update({"_id": player_id}, {"$set": {"game": ""}})
