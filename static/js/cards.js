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
        this.fetchCards();
        this.timer = setInterval(() => this.fetchCards(), 5000);
    }

    // function which is called when component about to be removed
    componentWillUnmount() {
        clearInterval(this.timer);
        this.timer = null;
    }

    fetchCards() {
        this.setState({cards: this.state.cards});
        // Make a request for cards for player
        axios.get('/game/' + getCookie("game_id") + '/get_cards')
        .then(response => {
            // handle success
            this.setState({cards: response.data})
        })
        .catch(error => {
            // handle error
            console.log(error);
            this.setState({cards: this.state.players})
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
            this.setState({cards: this.state.players})
        });
    }

    render() {
        return this.state.cards.map((card) =>
        <li key={ card._id }>
            <div className="card hand-card" onClick={(e) => this.playCard(card._id, e)}>
                <div className="card-body">
                    <h5 className="card-title">{ card.text }</h5>
                </div>
            </div>
        </li>);
    }
}

ReactDOM.render(
    <HandCards />,
    document.getElementById('hand-cards')
);
