from cards_against_humanity import db

card_in_play = db.Table("card_in_play", db.Model.metadata,
    db.Column("card_id", db.String(24), db.ForeignKey("card.id")),
    db.Column("player_id", db.String(8)),
    db.Column("game_id", db.String(5)),
    db.ForeignKeyConstraint(
        ["player_id", "game_id"],
        ["player_in_game.player_id", "player_in_game.game_id"]
    )
)

used_card = db.Table("used_card", db.Model.metadata,
    db.Column("card_id", db.String(24), db.ForeignKey("card.id")),
    db.Column("game_id", db.String(5), db.ForeignKey("game.id"))
)

class PlayerInGame(db.Model):
    __tablename__ = "player_in_game"
    player_id = db.Column(db.String(8), db.ForeignKey("player.id"), primary_key=True)
    game_id = db.Column(db.String(5), db.ForeignKey("game.id"), primary_key=True)
    state = db.Column(db.Integer, nullable=True)
    turn = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    player = db.relationship("Player", back_populates="games")
    game = db.relationship("Game", back_populates="players")
    cards = db.relationship("Card", secondary="card_in_play")
    played_card_id = db.Column(db.String(24), db.ForeignKey("card.id"))
    played_card = db.relationship("Card", foreign_keys=[played_card_id]) # many-to-one (parent)

    def __repr__(self):
        return "<PlayerInGame '{0}', '{1}'>".format(self.player_id, self.game_id)

    def as_json(self):
        return dict(player_id=self.player_id, game_id=self.game_id, state=self.state, turn=self.turn, score=self.score)

class Game(db.Model):
    __tablename__ = "game"
    id = db.Column(db.String(5), primary_key=True)
    state = db.Column(db.Integer, nullable=False)
    turn = db.Column(db.Integer, nullable=False)
    players = db.relationship("PlayerInGame", back_populates="game") # many-to-many (parent)
    black_card_id = db.Column(db.String(24), db.ForeignKey("card.id"))
    black_card = db.relationship("Card", foreign_keys=[black_card_id]) # many-to-one (parent)
    used_cards = db.relationship("Card", secondary="used_card") # many-to-many (parent)
    winning_card_id = db.Column(db.String(24), db.ForeignKey("card.id"))
    winning_card = db.relationship("Card", foreign_keys=[winning_card_id]) # many-to-one (parent)
    winner_id = db.Column(db.String(8), db.ForeignKey("player.id"))
    winner = db.relationship("Player", foreign_keys=[winner_id]) # many-to-one (parent)

    def __repr__(self):
        return "<Game '{0}'>".format(self.id)

    def as_json(self):
        return dict(id=self.id, state=self.state, turn=self.turn)

class Player(db.Model):
    __tablename__ = "player"
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    games = db.relationship("PlayerInGame", back_populates="player") # many-to-many (child)

    def __repr__(self):
        return "<Player '{0}', '{1}'>".format(self.id, self.name)

    def as_json(self):
        return dict(id=self.id, name=self.name)

class Card(db.Model):
    __tablename__ = "card"
    id = db.Column(db.String(24), primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    owners = db.relationship("PlayerInGame", secondary="card_in_play") # many-to-many (child)
    used_in = db.relationship("Game", secondary="used_card") # many-to-many (child)

    def __repr__(self):
        return "<Card '{1}'>".format(self.text)

    def as_json(self):
        return dict(id=self.id, text=self.text, type=self.type)


# create all databases from classes above
db.create_all()
