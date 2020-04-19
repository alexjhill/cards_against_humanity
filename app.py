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
def set_name(): # set user name if user hasn't done so before
    if request.method == 'POST':
        name = request.form.get("name")
        user_id = create_id(8)
        user = {
            "_id": user_id,
            "name": name,
            "cards": []
        }
        db.users.insert_one(user)
        game_id = request.cookies.get('game_id')
        resp = make_response(redirect(url_for("game", game_id = game_id)))
        resp.set_cookie('user_id', user_id)
        return resp
    else:
        return render_template("set-name.html")

@app.route('/new_game')
def new_game():
    game_id = create_id(5)
    while db.games.find_one({"_id": game_id}) is not None:
        logger.warning("Game ID already exists")
        game_id = create_id(5)
    new_game = {"_id": game_id, "users" : []}
    db.games.insert_one(new_game)
    return redirect(url_for("game", game_id = game_id))



@app.route('/game/<game_id>')
def game(game_id):
    user_id = request.cookies.get('user_id')
    # if user has not been here before
    if user_id is None:
        # create new name
        response = redirect(url_for("set_name"))
        response.set_cookie('game_id', game_id)
        return response
    else:
        # add user to game
        user = db.users.find_one({"_id": user_id})
        db.games.update({"_id": game_id}, {"$push": {"users": user}})

        # get game object
        game = db.games.find_one({"_id": game_id})

        # get users
        users = game.get("users")
        if not user.get("cards"):
            random_cards = []
            for i in range(0, db.cards.count()):
                random_cards.append(db.cards.find().skip(i).limit(1)[0])
            db.users.update_one({"_id": user_id}, {"$set": {"cards": random_cards}})
        cards = db.users.find_one({"_id": user_id}).get("cards")
        return render_template("game.html", game = game, users = users, cards = cards)
