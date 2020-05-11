class HandCards extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            cards: []
        };
    }

    // function which is called when component is added
    componentDidMount() {
        // get cards
        this.fetchCards()
        this.timer = setInterval(() => this.fetchCards(), 5000);
    }

    // function which is called when component about to be removed
    componentWillUnmount() {
        clearInterval(this.timer);
        this.timer = null;
    }

    fetchCards() {
        // Make a request for cards for player
        axios.get('/game/' + getCookie("game_id") + '/get_cards')
        .then(response => {
            // handle success
            this.setState({
                cards: response.data
            })
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    playCard(id, e) {
        axios.post('/game/' + getCookie("game_id") + '/play_card', {
            player: getCookie("player_id"),
            card_id: id
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    pickWinner(playerId, e) {
        axios.post('/game/' + getCookie("game_id") + '/pick_winner', {
            player: playerId
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    render() {
        if (this.props.gameState == 0) {
            if (this.props.playerState == 0) {
                return (
                    this.state.cards.map((card) =>
                        <li key={ card.id }>
                            <div className="card hand-card" onClick={(e) => this.playCard(card.id, e)}>
                                <div className="card-body">
                                    <h5 className="card-title">{ card.text }</h5>
                                </div>
                            </div>
                        </li>
                    )
                )
            } else if (this.props.playerState == 2) {
                return <h4>Fish</h4>
            } else {
                return <h4>Game state/player state combo error...</h4>
            }
        } else if (this.props.gameState == 1) {
            if (this.props.playerState == 0) {
                return (
                    this.state.cards.map((card) =>
                        <li key={ card.id }>
                            <div className="card hand-card" onClick={(e) => this.playCard(card.id, e)}>
                                <div className="card-body">
                                    <h5 className="card-title">{ card.text }</h5>
                                </div>
                            </div>
                        </li>
                    )
                )
            } else if (this.props.playerState == 1) {
                return (
                    <h4>Waiting for other players to play...</h4>
                )
            } else if (this.props.playerState == 2) {
                return (
                    <h4>Waiting for players to play...</h4>
                )
            } else {
                return (
                    <h4>Player state error...</h4>
                )
            }
        } else if (this.props.gameState == 2) {
            if (this.props.playerState == 0) { // card playing
                return (
                    <h4>Player state error...</h4>
                )
            } else if (this.props.playerState == 1) { // card played
                return (
                    <h4>Waiting for card tzar to pick a card...</h4>
                )
            } else  if (this.props.playerState == 2) { // card tzar
                return (
                    this.props.playedCards.map((cardPlay) =>
                        <li key={ cardPlay.player }>
                            <div className="card hand-card" onClick={(e) => this.pickWinner(cardPlay.player, e)}>
                                <div className="card-body">
                                    <h5 className="card-title">{ cardPlay.card }</h5>
                                </div>
                            </div>
                        </li>
                    )
                )
            }
        }
    }
}
