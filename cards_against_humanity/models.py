from cards_against_humanity import db

card_in_play = db.Table('card_in_play', db.Model.metadata,
    db.Column('card_id', db.String(24), db.ForeignKey('card.id')),
    db.Column('player_id', db.String(8), db.ForeignKey('player.id'))
)

used_card = db.Table('used_card', db.Model.metadata,
    db.Column('card_id', db.String(24), db.ForeignKey('card.id')),
    db.Column('game_id', db.String(5), db.ForeignKey('game.id'))
)

player_in_game = db.Table('player_in_game', db.Model.metadata,
    db.Column('player_id', db.String(8), db.ForeignKey('player.id')),
    db.Column('game_id', db.String(5), db.ForeignKey('game.id')),
    db.Column('state', db.Integer, nullable=True),
    db.Column('game_position', db.Integer, nullable=True),
    db.Column('score', db.Integer, nullable=True),
    played_card = db.relationship('Card') # many-to-one (parent)
)

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.String(5), primary_key=True)
    state = db.Column(db.Integer, nullable=False)
    turn = db.Column(db.Integer, nullable=False)
    players = db.relationship('Player', secondary='player_in_game') # many-to-many (parent)
    black_card_id = db.Column(db.String(24), db.ForeignKey('card.id'))
    black_card = db.relationship('Card', foreign_keys=[black_card_id]) # many-to-one (parent)
    used_cards = db.relationship('Card', secondary='used_card') # many-to-many (parent)
    winning_card_id = db.Column(db.String(24), db.ForeignKey('card.id'))
    winning_card = db.relationship('Card', foreign_keys=[winning_card_id]) # many-to-one (parent)
    winner_id = db.Column(db.String(8), db.ForeignKey('player.id'))
    winner = db.relationship('Player', foreign_keys=[winner_id]) # many-to-one (parent)

    def __repr__(self):
        return '<Game %r>' % self.id

    def as_json(self):
        return dict(id=self.id, state=self.state)

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    games = db.relationship('Game', secondary='player_in_game') # many-to-many (child)

    def __repr__(self):
        return '<Player %r>' % self.name

    def as_json(self):
        return dict(id=self.id, name=self.name)

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    owners = db.relationship('Player', secondary='card_in_play') # many-to-many (child)
    used_in = db.relationship('Game', secondary='used_card') # many-to-many (child)

    def __repr__(self):
        return '<Card %r>' % self.text

    def as_json(self):
        return dict(id=self.id, text=self.text, type=self.type)


# create all databases from classes above
db.create_all()
