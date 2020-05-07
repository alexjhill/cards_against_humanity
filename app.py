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
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import random
import coloredlogs, logging
import json

app = Flask(__name__)

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
conn_str = 'mysql+pymysql://unfbbwlp7m40iqvv:Th8cO1VKB9sUy94XFYQg@b1seqbavm975g4dqrctm-mysql.services.clever-cloud.com/b1seqbavm975g4dqrctm'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app)



class DeckCard(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Deck Card %r>' % self.text

    def as_json(self):
        return dict(id=self.id, text=self.text, type=self.type)

class HandCard(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    player = db.Column(db.String(8), db.ForeignKey('player.id'), nullable=False)
    game = db.Column(db.String(5), db.ForeignKey('game.id'), nullable=False)

    def __repr__(self):
        return '<Hand Card %r>' % self.text

    def as_json(self):
        return dict(id=self.id, text=self.text, player=self.player, game=self.game)

class Game(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    state = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Game %r>' % self.id

    def as_json(self):
        return dict(id=self.id, state=self.state)

class Player(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    game = db.Column(db.String(5), db.ForeignKey('game.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Player %r>' % self.name

    def as_json(self):
        return dict(id=self.id, name=self.name, state=self.state, game=self.game, score=self.score)

# create all databases from classes above
db.create_all()



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
        new_card = DeckCard(id=create_id(24), text=text, type=0)
        db.session.add(new_card)
        db.session.commit()
        return render_template("add-cards.html")
    else:
        return render_template("add-cards.html")

@app.route('/set_name', methods=['GET', 'POST'])
def set_name(): # set player name if player hasn't done so before
    if request.method == 'POST':

        # create new player
        name = request.form.get("name")
        player_id = create_id(8)
        new_player = Player(id=player_id, name=name, state=0, score=0)
        db.session.add(new_player)
        db.session.commit()

        # redirect back to game
        game_id = request.cookies.get('game_id')
        resp = make_response(redirect(url_for("game", game_id = game_id)))
        resp.set_cookie('player_id', player_id)
        return resp
    else:
        return render_template("set-name.html")

@app.route('/new_game')
def new_game(): # create new game
    # create new unique game
    game_id = create_id(5)
    while Game.query.filter_by(id=game_id).first() is not None:
        logger.warning("Game ID already exists")
        game_id = create_id(5)
    new_game = Game(id=game_id, state=0)
    db.session.add(new_game)
    db.session.commit()

    return redirect(url_for("game", game_id = game_id))



# @app.route('/game/<game_id>/new_round')
# def new_round(game_id):
#     # wipe played cards and reset game state
#     db.games.update_one({"_id": game_id}, {"$set": {"state": 0, "played_cards": []}})
#     # update players state
#     db.players.update({"game": game_id}, {"$set": {"state": 0}})
#
#     return redirect(url_for("game", game_id = game_id))



@app.route('/game/<game_id>')
def game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if game:
        player_id = request.cookies.get('player_id')
        # if player has not been here before
        if player_id is None:
            # create new name
            resp = make_response(redirect(url_for("set_name")))
            resp.set_cookie('game_id', game_id)
            return resp
        else:
            # add game to player
            player = Player.query.filter_by(id=player_id).first()
            player.game = game_id
            db.session.commit()

            # return game page
            resp = make_response(render_template("game.html"))
            resp.set_cookie('game_id', game_id)
            return resp
    else:
        return redirect(url_for("home"))

@app.route('/game/<game_id>/get_game')
def get_game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    player_id = request.cookies.get('player_id')
    player_state = Player.query.filter_by(id=player_id).first().state

    # convert to JSON and return
    data = [game.as_json(), player_state]
    logger.debug(data)
    return json.dumps(data)

@app.route('/game/<game_id>/get_players')
def get_players(game_id): # return all players matching this game
    players = Player.query.filter_by(game=game_id)

    # convert to JSON and return
    data = []
    for player in players:
        data.append(player.as_json())
    return json.dumps(data)

@app.route('/game/<game_id>/get_cards')
def get_cards(game_id): # return cards for this player
    player_id = request.cookies.get('player_id')

    # find cards for this player in this game
    player_cards = HandCard.query.filter_by(player=player_id, game=game_id).all()

    # if player doesn't have cards get random ones
    if not player_cards:
        random_cards = DeckCard.query.filter_by(type=0).order_by(func.random()).limit(10).all()
        for random_card in random_cards:
            new_card = HandCard(id=random_card.id, text=random_card.text, player=player_id, game=game_id)
            db.session.add(new_card)
        db.session.commit()
        player_cards = HandCard.query.filter_by(player=player_id, game=game_id).all()

    # convert to JSON and return
    data = []
    for card in player_cards:
        data.append(card.as_json())
    return json.dumps(data)

@app.route('/game/<game_id>/play_card', methods=['POST'])
def play_card(game_id):
    player_id = request.cookies.get('player_id')

    # get played card
    card_play = json.loads(request.data)
    card_id = card_play.get("card_id")

    # remove played card from player
    HandCard.query.filter_by(id=card_id, game=game_id).delete()

    # update player state
    player = Player.query.filter_by(id=player_id).first()
    player.state = 1

    # give player a unique new card
    deck_card = DeckCard.query.filter_by(type=0).order_by(func.random()).first()
    new_card = HandCard(id=deck_card.id, text=deck_card.text, player=player_id, game=game_id)
    db.session.add(new_card)

    # get new user cards
    new_user_cards = HandCard.query.filter_by(player=player_id, game=game_id).all()

    # if no players left to play, next game state
    still_to_play = Player.query.filter_by(game=game_id, state=0).count()
    if still_to_play == 0:
        game = Game.query.filter_by(id=game_id)
        game.state = 2

    db.session.commit()

    # convert to JSON and return
    data = []
    for card in new_user_cards:
        data.append(card.as_json())
    return json.dumps(data)




# @app.route('/game/remove_player', methods=['POST'])
# def remove_player():
    # logger.debug("test")
    # player_id = request.cookies.get('player_id')
    # db.players.update({"_id": player_id}, {"$set": {"game": ""}})
