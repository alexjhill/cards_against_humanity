from cards_against_humanity import app
from flask import request, redirect, url_for
import json
from sqlalchemy import func, or_

from cards_against_humanity.models import *
from cards_against_humanity.views import logger


@app.route('/api/<game_id>/get_game')
def get_game(game_id):
    game = Game.query.filter_by(id=game_id).first()
    player_id = request.cookies.get('player_id')
    player_state = Player.query.filter_by(id=player_id).first().state

    # get played cards from players who have played
    played_cards = []
    for player in game.players:
        if player.state == 1:
            played_cards.append({"player": player.id, "card": player.played_card.as_json()})

    data = [game.as_json(), player_state, played_cards]

    if game.state == 3:
        # get the winner
        winner = game.winner.as_json()
        # get the winning card
        winning_card = game.winning_card.as_json()
        data.append(winner)
        data.append(winning_card)

    # convert to JSON and return
    return json.dumps(data)

@app.route('/api/<game_id>/get_players')
def get_players(game_id): # return all players matching this game
    players = Player.query.filter_by(game_id=game_id).all()

    # convert to JSON and return
    data = []
    for player in players:
        data.append(player.as_json())
    return json.dumps(data)

@app.route('/api/<game_id>/new_black_card')
def new_black_card(game_id): # return black card for this game
    black_card = Card.query.filter_by(type=1).order_by(func.random()).first()
    return black_card.as_json()

@app.route('/api/<game_id>/pick_black_card', methods=['POST'])
def pick_black_card(game_id): # pick black card for this game
    card_id = json.loads(request.data).get("card_id")
    picked_black_card = Card.query.filter_by(id=card_id).first()
    game = Game.query.filter_by(id=game_id).first()
    game.black_card = picked_black_card
    game.state = 1
    game.used_cards.append(picked_black_card)
    db.session.commit()
    return ('', 204)

@app.route('/api/<game_id>/get_black_card')
def get_black_card(game_id): # return black card for this game
    game = Game.query.filter_by(id=game_id).first()
    black_card = game.black_card
    return black_card.as_json()

@app.route('/api/<game_id>/get_cards')
def get_cards(game_id): # return cards for this player
    player_id = request.cookies.get('player_id')

    # find cards for this player in this game
    player = Player.query.filter_by(id=player_id).first()

    # if player doesn't have cards get random ones
    if not player.cards:
        game = Game.query.filter_by(id=game_id).first()
        random_cards = Card.query.outerjoin(used_card).outerjoin(Game).filter(Card.type == 0).filter(or_(used_card.c.game_id == None, used_card.c.game_id != game_id)).order_by(func.random()).limit(10).all()
        for random_card in random_cards:
            player.cards.append(random_card)
            game.used_cards.append(random_card)
        db.session.commit()

    # convert to JSON and return
    data = []
    for card in player.cards:
        data.append(card.as_json())
    return json.dumps(data)

@app.route('/api/<game_id>/play_card', methods=['POST'])
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
    player.played_card = card

    # give player a unique new card and add to used cards
    random_card = Card.query.outerjoin(used_card).outerjoin(Game).filter(Card.type == 0).filter(or_(used_card.c.game_id == None, used_card.c.game_id != game_id)).order_by(func.random()).first()
    if random_card:
        player.cards.append(random_card)
        game = player.game
        game.used_cards.append(random_card)
    else:
        logger.debug("no cards that haven't been used left")

    # if no players left to play, next game state
    still_to_play = Player.query.filter_by(game_id=game_id, state=0).count()
    if still_to_play == 0:
        game.state = 2

    db.session.commit()

    # convert to JSON and return
    data = []
    for card in player.cards:
        data.append(card.as_json())
    return json.dumps(data)

@app.route('/api/<game_id>/pick_winner', methods=['POST'])
def pick_winner(game_id):
    winner_id = json.loads(request.data).get("player")
    winning_card_id = json.loads(request.data).get("card")
    winner = Player.query.filter_by(id=winner_id).first()
    winning_card = Card.query.filter_by(id=winning_card_id).first()
    winner.score += 1
    game = Game.query.filter_by(id=game_id).first()
    game.winner = winner
    game.winning_card = winning_card
    game.state = 3
    db.session.commit()
    return ('', 204)


@app.route('/api/<game_id>/new_round', methods=['POST'])
def new_round(game_id):
    # wipe played cards and reset game state
    game = Game.query.filter_by(id=game_id).first()
    game.state = 0

    # update players state
    players = Player.query.filter_by(game_id=game_id).all()
    for player in players:
        player.state = 0
        player.played_card = None

    # set new card tzar
    card_tzar = Player.query.filter_by(game_id=game_id).first()
    card_tzar.state = 2

    db.session.commit()

    return redirect(url_for("game", game_id = game_id))
