from cards_against_humanity import db

card_in_play = db.Table('card_in_play', db.Model.metadata,
    db.Column('card_id', db.String(24), db.ForeignKey('card.id')),
    db.Column('player_id', db.String(8), db.ForeignKey('player.id'))
)

used_card = db.Table('used_card', db.Model.metadata,
    db.Column('card_id', db.String(24), db.ForeignKey('card.id')),
    db.Column('game_id', db.String(5), db.ForeignKey('game.id'))
)

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    owners = db.relationship('Player', secondary='card_in_play')
    games_used_in = db.relationship('Game', secondary='used_card')

    def __repr__(self):
        return '<Card %r>' % self.text

    def as_json(self):
        return dict(id=self.id, text=self.text, type=self.type)

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.String(5), primary_key=True)
    state = db.Column(db.Integer, nullable=False)
    black_card = db.Column(db.String(24), db.ForeignKey('card.id'), nullable=True)
    players = db.relationship('Player')
    used_cards = db.relationship('Card', secondary='used_card')

    def __repr__(self):
        return '<Game %r>' % self.id

    def as_json(self):
        return dict(id=self.id, state=self.state, black_card=self.black_card)

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    game = db.Column(db.String(5), db.ForeignKey('game.id'), nullable=True)
    cards = db.relationship('Card', secondary='card_in_play')
    played_card = db.Column(db.String(24), db.ForeignKey('card.id'), nullable=True)

    def __repr__(self):
        return '<Player %r>' % self.name

    def as_json(self):
        return dict(id=self.id, name=self.name, state=self.state, game=self.game, score=self.score)


# create all databases from classes above
db.create_all()
