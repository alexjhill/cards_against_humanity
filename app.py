'''
GAME STATES
-1 = error
0 = black card selection
1 = card playing
2 = winner selection

PLAYER STATES
-1 = error
0 = card playing
1 = card played
2 = card tzar

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
# db 1
conn_str = 'mysql+pymysql://unfbbwlp7m40iqvv:Th8cO1VKB9sUy94XFYQg@b1seqbavm975g4dqrctm-mysql.services.clever-cloud.com/b1seqbavm975g4dqrctm'
# db 2 (backup)
# conn_str = 'mysql+pymysql://upbx80jfe46euwjn:u1PKoKQrwlh4WE47aHM7@bzubvxk0tyjehwx4q0og-mysql.services.clever-cloud.com/bzubvxk0tyjehwx4q0og'
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
db = SQLAlchemy(app)

cards_in_play = db.Table('cards_in_play', db.Model.metadata,
    db.Column('player', db.String(8), db.ForeignKey('player.id')),
    db.Column('card', db.String(24), db.ForeignKey('card.id')),
    db.Column('game', db.String(5), db.ForeignKey('game.id'))
)

class Card(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Card %r>' % self.text

    def as_json(self):
        return dict(id=self.id, text=self.text, type=self.type)

class Game(db.Model):
    id = db.Column(db.String(5), primary_key=True)
    state = db.Column(db.Integer, nullable=False)
    black_card = db.Column(db.String(24), db.ForeignKey('card.id'), nullable=False)
    players = db.relationship("Player")
    cards = db.relationship("Card", secondary=cards_in_play)

    def __repr__(self):
        return '<Game %r>' % self.id

    def as_json(self):
        return dict(id=self.id, state=self.state, black_card=self.black_card)

class Player(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    game = db.Column(db.String(5), db.ForeignKey('game.id'), nullable=True)
    cards = db.relationship("Card", secondary=cards_in_play)
    played_card = db.Column(db.String(24), db.ForeignKey('card.id'), nullable=True)

    def __repr__(self):
        return '<Player %r>' % self.name

    def as_json(self):
        return dict(id=self.id, name=self.name, state=self.state, game=self.game, score=self.score)


# create all databases from classes above
# db.create_all()



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
        new_card = Card(id=create_id(24), text=text, type=0)
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
    black_card = Card.query.filter_by(type=1).order_by(func.random()).first().id
    new_game = Game(id=game_id, state=0, black_card=black_card)
    db.session.add(new_game)
    db.session.commit()

    return redirect(url_for("game", game_id = game_id))



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

    played_cards = []
    for player in game.players:
        if player.state == 1:
            played_cards.append({"player": player.id, "card": Card.query.filter_by(id=player.played_card).first().text})

    # convert to JSON and return
    data = [game.as_json(), player_state, played_cards]
    return json.dumps(data)

@app.route('/game/<game_id>/get_players')
def get_players(game_id): # return all players matching this game
    players = Player.query.filter_by(game=game_id)

    # convert to JSON and return
    data = []
    for player in players:
        data.append(player.as_json())
    return json.dumps(data)

@app.route('/game/<game_id>/get_black_card')
def get_black_card(game_id): # return black card for this game
    game = Game.query.filter_by(id=game_id).first()
    black_card = Card.query.filter_by(id=game.black_card).first()
    return black_card.as_json()

@app.route('/game/<game_id>/new_black_card')
def new_black_card(game_id): # return black card for this game
    black_card = Card.query.filter_by(type=1).order_by(func.random()).first()
    return black_card.as_json()

@app.route('/game/<game_id>/pick_black_card', methods=['POST'])
def pick_black_card(game_id): # pick black card for this game
    card_id = card_play = json.loads(request.data).get("card_id")
    black_card = Card.query.filter_by(id=card_id).first()
    game = Game.query.filter_by(id=game_id).first()
    game.black_card = black_card.id
    game.state = 1
    db.session.commit()
    return ('', 204)

@app.route('/game/<game_id>/get_cards')
def get_cards(game_id): # return cards for this player
    player_id = request.cookies.get('player_id')

    # find cards for this player in this game
    player = Player.query.filter_by(id=player_id).first()

    # if player doesn't have cards get random ones
    if not player.cards:
        random_cards = Card.query.filter_by(type=0).order_by(func.random()).limit(10).all()
        for random_card in random_cards:
            player.cards.append(random_card)
        db.session.commit()

    # convert to JSON and return
    data = []
    for card in player.cards:
        data.append(card.as_json())
    return json.dumps(data)

@app.route('/game/<game_id>/play_card', methods=['POST'])
def play_card(game_id):
    player_id = request.cookies.get('player_id')

    # get played card
    card_play = json.loads(request.data)
    card_id = card_play.get("card_id")
    card = Card.query.filter_by(id=card_id).first()

    # remove played card from player
    player = Player.query.filter_by(id=player_id).first()
    player.cards.remove(card)

    # update player state and played card
    player.state = 1
    player.played_card = card_id

    # give player a unique new card
    new_card = Card.query.filter_by(type=0).order_by(func.random()).first()
    player.cards.append(new_card)

    # if no players left to play, next game state
    still_to_play = Player.query.filter_by(game=game_id, state=0).count()
    if still_to_play == 0:
        game.state = 2

    db.session.commit()


    # convert to JSON and return
    data = []
    for card in player.cards:
        data.append(card.as_json())
    return json.dumps(data)

@app.route('/game/<game_id>/pick_winner', methods=['POST'])
def pick_winner(game_id):
    winner_id = json.loads(request.data).get("player")
    winner = Player.query.filter_by(id=winner_id).first()
    winner.score += 1

    db.session.commit()

    return redirect(url_for("new_round", game_id = game_id))

@app.route('/game/<game_id>/new_round')
def new_round(game_id):
    # wipe played cards and reset game state
    game = Game.query.filter_by(id=game_id).first()
    game.state = 0
    game.black_card = Card.query.filter_by(type=1).order_by(func.random()).first().id

    # update players state
    players = Player.query.filter_by(game=game_id).all()
    for player in players:
        player.state = 0
        player.played_card = None

    # set new card tzar
    card_tzar = Player.query.filter_by(game=game_id).first()
    card_tzar.state = 2

    db.session.commit()

    return redirect(url_for("game", game_id = game_id))
