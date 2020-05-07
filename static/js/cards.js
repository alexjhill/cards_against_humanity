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
        console.log(id)
        axios.post('/game/' + getCookie("game_id") + '/play_card', {
            player: getCookie("player_id"),
            card_id: id
        })
        .catch(error => {
            // handle error
            console.log(error);
        });
    }

    render() {
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
        } else if (this.props.gameState == 2) {
            return (
                <h4>Waiting for card tzar to pick winner...</h4>
            )
        } else {
            return (
                <h4>Error...</h4>
            )
        }
    }
}
