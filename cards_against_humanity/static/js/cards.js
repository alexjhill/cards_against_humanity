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
        axios.get('/api/' + getCookie("game_id") + '/get_cards')
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

    playCard(cardId, e) {
        this.props.updateGame(1, 1)
        axios.post('/api/' + getCookie("game_id") + '/play_card', {
            player: getCookie("player_id"),
            card_id: cardId
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    pickWinner(playerId, cardId, e) {
        this.props.updateGame(-1, 2)
        axios.post('/api/' + getCookie("game_id") + '/pick_winner', {
            player: playerId,
            card: cardId
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
                            <div className="card hand-card">
                                <div className="card-body">
                                    <p className="card-title">{ card.text }</p>
                                </div>
                            </div>
                        </li>
                    )
                )
            } else if (this.props.playerState == 2) {
                return <h4 className="text-muted">Choose a black card</h4>
            } else {
                return <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
            }
        } else if (this.props.gameState == 1) {
            if (this.props.playerState == 0) {
                return (
                    this.state.cards.map((card) =>
                        <li key={ card.id }>
                            <div className="card hand-card" onClick={(e) => this.playCard(card.id, e)}>
                                <div className="card-body">
                                    <p className="card-title">{ card.text }</p>
                                </div>
                            </div>
                        </li>
                    )
                )
            } else if (this.props.playerState == 1) {
                return (
                    <h4 className="text-muted">Waiting for other players to play their cards...</h4>
                )
            } else if (this.props.playerState == 2) {
                return (
                    <h4 className="text-muted">Waiting for players to play their cards...</h4>
                )
            } else {
                return (
                    <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
                )
            }
        } else if (this.props.gameState == 2) {
            if (this.props.playerState == 0) { // card playing
                return (
                    <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
                )
            } else if (this.props.playerState == 1) { // card played
                return (
                    <h4 className="text-muted">Waiting for card tzar to pick a winner...</h4>
                )
            } else  if (this.props.playerState == 2) { // card tzar
                return (
                    this.props.playedCards.map((cardPlay) =>
                        <li key={ cardPlay.player }>
                            <div className="card hand-card" onClick={(e) => this.pickWinner(cardPlay.player, cardPlay.card.id, e)}>
                                <div className="card-body">
                                    <p className="card-title">{ cardPlay.card.text }</p>
                                </div>
                            </div>
                        </li>
                    )
                )
            }
        } else if (this.props.gameState == 3) { // winner page
            return (
                <div className="winning-card">
                    <div className="card winning-card">
                        <div className="card-body">
                            <p className="card-title">{ this.props.winningCard.text }</p>
                        </div>
                    </div>
                </div>
            )
        } else {
            return <div className="loading-sprite"><div></div><div></div><div></div><div></div></div>
        }
    }
}
